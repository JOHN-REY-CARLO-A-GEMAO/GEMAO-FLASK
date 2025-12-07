import os
import re
import ast
import threading
import time
from typing import Dict, Any, List

from .db import get_db, log_audit_action

GAMES_DIR = os.path.join(os.path.dirname(__file__), 'games')
WATCH_INTERVAL_SECONDS = 15

def _list_game_files() -> List[str]:
    files = []
    for name in os.listdir(GAMES_DIR):
        if not name.lower().endswith('.py'):
            continue
        if name in {'__init__.py', 'base_game.py'}:
            continue
        files.append(os.path.join(GAMES_DIR, name))
    return files

def _rel_path(path: str) -> str:
    try:
        return os.path.relpath(path, GAMES_DIR).replace('\\', '/')
    except Exception:
        return path

def parse_game_metadata(file_path: str) -> Dict[str, Any]:
    name = os.path.splitext(os.path.basename(file_path))[0]
    description = ''
    version = None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            mod = ast.parse(content)
            doc = ast.get_docstring(mod) or ''
            description = doc.strip()
        except Exception:
            description = ''
        m = re.search(r"super\s*\.__init__\(\s*['\"]([^'\"]+)['\"]\s*,\s*\d+\s*,\s*\d+\s*\)", content)
        if m:
            name = m.group(1).strip()
        vm = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
        if vm:
            version = vm.group(1).strip()
    except Exception:
        pass
    return {
        'name': name,
        'description': description,
        'version': version,
        'file_path': _rel_path(file_path),
    }

def sync_games(actor_id: int | None = None) -> Dict[str, Any]:
    result = {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 0, 'details': []}
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, name, description, file_path, image_path FROM games")
        rows = cur.fetchall()
        cur.close()
        by_path = {r['file_path']: r for r in rows if r.get('file_path')}
        by_name = {}
        for r in rows:
            if r.get('name'):
                by_name[r['name']] = r
        files = _list_game_files()
        wcur = conn.cursor()
        for fp in files:
            meta = parse_game_metadata(fp)
            rel = meta['file_path']
            nm = meta['name']
            desc = meta['description']
            try:
                if rel in by_path:
                    row = by_path[rel]
                    need_upd = False
                    new_name = row['name']
                    new_desc = row['description']
                    if nm and nm != row['name']:
                        new_name = nm
                        need_upd = True
                    if desc and desc != (row['description'] or ''):
                        new_desc = desc
                        need_upd = True
                    if need_upd:
                        wcur.execute(
                            "UPDATE games SET name = %s, description = %s WHERE id = %s",
                            (new_name, new_desc, row['id'])
                        )
                        result['updated'] += 1
                        result['details'].append({'file': rel, 'action': 'updated'})
                    else:
                        result['skipped'] += 1
                        result['details'].append({'file': rel, 'action': 'skipped'})
                elif nm in by_name:
                    row = by_name[nm]
                    wcur.execute(
                        "UPDATE games SET file_path = %s WHERE id = %s",
                        (rel, row['id'])
                    )
                    result['updated'] += 1
                    result['details'].append({'file': rel, 'action': 'linked'})
                else:
                    wcur.execute(
                        "INSERT INTO games (name, description, file_path) VALUES (%s, %s, %s)",
                        (nm, desc, rel)
                    )
                    result['inserted'] += 1
                    result['details'].append({'file': rel, 'action': 'inserted'})
            except Exception:
                result['errors'] += 1
                result['details'].append({'file': rel, 'action': 'error'})
        conn.commit()
        try:
            summary = f"inserted={result['inserted']}, updated={result['updated']}, skipped={result['skipped']}, errors={result['errors']}"
            log_audit_action(actor_id, None, 'sync_games', summary)
        except Exception:
            pass
    except Exception:
        result['errors'] += 1
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
    return result

class _Watcher(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self._stop = threading.Event()
        self._app = app
    def run(self):
        while not self._stop.is_set():
            try:
                with self._app.app_context():
                    sync_games(None)
            except Exception:
                pass
            self._stop.wait(WATCH_INTERVAL_SECONDS)
    def stop(self):
        self._stop.set()

_watcher = None

def start_watcher(app):
    global _watcher
    if _watcher is None:
        _watcher = _Watcher(app)
        _watcher.start()

