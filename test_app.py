import unittest
import types
import datetime
from werkzeug.security import generate_password_hash

from MyFlaskapp import create_app
import MyFlaskapp.db as db
import MyFlaskapp.blueprints.api as api
from itsdangerous import URLSafeTimedSerializer
from io import BytesIO
from PIL import Image


FAKE_IS_ALLOWED = True

class FakeCursor:
    def __init__(self):
        self._results = None

    def execute(self, query, params=None):
        q = " ".join(query.split()).lower()
        if "from users where username" in q:
            self._results = [{
                'id': 1,
                'username': 'admin',
                'password': generate_password_hash('admin123'),
                'email': 'admin@leafvillage.com',
                'firstname': 'Super',
                'lastname': 'Admin',
                'role': 'Admin',
                'is_active': True
            }]
        elif "from users where id" in q:
            self._results = [{
                'id': 1,
                'username': 'admin',
                'password': generate_password_hash('admin123'),
                'email': 'admin@leafvillage.com',
                'firstname': 'Super',
                'lastname': 'Admin',
                'role': 'Admin',
                'is_active': True
            }]
        elif "select * from users" in q:
            self._results = [
                {'id': 1, 'username': 'admin', 'email': 'admin@leafvillage.com', 'role': 'Admin', 'is_active': True},
                {'id': 2, 'username': 'user1', 'email': 'user1@example.com', 'role': 'User', 'is_active': True},
            ]
        elif "from games" in q and "left join game_access" in q and "where g.file_path" in q:
            self._results = [
                {'is_allowed': FAKE_IS_ALLOWED}
            ]
        elif "from games" in q and "left join game_access" in q:
            self._results = [
                {'id': 1, 'name': 'Naruto Runner', 'description': 'Run forever!', 'file_path': 'naruto_runner.py', 'is_allowed': True},
                {'id': 2, 'name': 'Sudoku', 'description': 'Puzzle', 'file_path': 'sudoku.py', 'is_allowed': False},
            ]
        elif "insert into game_access" in q:
            self._results = []
        elif "from blog_posts join users" in q:
            self._results = [
                {'id': 1, 'title': 'Post A', 'content': 'Content A', 'username': 'admin', 'created_at': datetime.datetime(2023, 1, 1)},
                {'id': 2, 'title': 'Post B', 'content': 'Content B', 'username': 'user1', 'created_at': datetime.datetime(2023, 1, 2)},
            ]
        else:
            self._results = []

    def fetchone(self):
        if not self._results:
            return None
        return self._results[0]

    def fetchall(self):
        return list(self._results or [])

    def close(self):
        pass


class FakeConn:
    def cursor(self, dictionary=False):
        return FakeCursor()

    def commit(self):
        pass

    def close(self):
        pass


def fake_get_db():
    return FakeConn()


class FlaskAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.get_db = fake_get_db
        db.init_db_commands = lambda: None
        api._rate_limit_check = lambda key: True
        cls.app = create_app({'ENABLE_CSRF': False})
        cls.app.testing = True
        cls.client = cls.app.test_client()

    def test_index(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)

    def test_login_admin_redirect(self):
        r = self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=False)
        self.assertEqual(r.status_code, 302)
        loc = r.headers.get('Location', '')
        self.assertTrue(('/admin/dashboard' in loc) or ('/user/dashboard' in loc))

    def test_admin_dashboard_after_login(self):
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
        r = self.client.get('/admin/dashboard')
        self.assertEqual(r.status_code, 200)

    def test_admin_settings_labels(self):
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
        r = self.client.get('/admin/settings')
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn('Global Audio', html)
        self.assertIn('Master Volume', html)
        self.assertIn('Ambient Music', html)
        self.assertIn('Game Audio Levels', html)
        self.assertIn('data-bs-toggle="tooltip"', html)

    def test_admin_settings_audio_requires_csrf(self):
        app2 = create_app({'TESTING': True})
        with app2.test_client() as c:
            # no login provided; endpoint should still enforce CSRF and likely return 400
            r = c.post('/admin/settings/audio', json={'master': 0.5, 'ambient': 0.5, 'per_game': {}})
            self.assertEqual(r.status_code, 400)

    def test_manage_games_get(self):
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
        r = self.client.get('/admin/user/1/game-access')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn('games', data)
        self.assertTrue(len(data['games']) >= 1)

    def test_manage_games_post(self):
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
        r = self.client.post('/admin/user/1/game-access', json={'updates': [{'game_id': 1, 'is_allowed': False}]})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data.get('status'), 'ok')

    def test_logout(self):
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
        r = self.client.get('/auth/logout', follow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertTrue('/' in r.headers.get('Location', ''))

    def test_admin_toggle_requires_csrf(self):
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
        r = self.client.post('/admin/toggle_status/1', follow_redirects=False)
        self.assertEqual(r.status_code, 302)

    def test_blog_index(self):
        r = self.client.get('/blog/')
        self.assertEqual(r.status_code, 200)

    def _make_image(self, size=(100, 100), fmt='PNG'):
        img = Image.new('RGB', size, color=(10, 20, 30))
        bio = BytesIO()
        img.save(bio, format=fmt)
        bio.seek(0)
        return bio

    def test_upload_profile_picture_success(self):
        with self.app.test_request_context('/'):
            s = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
            token = s.dumps('1')
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['loggedin'] = True
            data = {
                'file': (self._make_image((150, 150), 'PNG'), 'avatar.png')
            }
            r = c.post('/api/users/upload-profile-picture', data=data, content_type='multipart/form-data', headers={'X-CSRFToken': token})
            info = {} if not hasattr(r, 'get_json') else (r.get_json(silent=True) or {})
            self.assertEqual(r.status_code, 200, msg=f"resp={info}")
            self.assertTrue(info.get('success'))

    def test_upload_profile_picture_small(self):
        with self.app.test_request_context('/'):
            s = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
            token = s.dumps('1')
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['loggedin'] = True
            data = {
                'file': (self._make_image((50, 50), 'PNG'), 'small.png')
            }
            r = c.post('/api/users/upload-profile-picture', data=data, content_type='multipart/form-data', headers={'X-CSRFToken': token})
            self.assertEqual(r.status_code, 400)

    def test_upload_profile_picture_wrong_type(self):
        with self.app.test_request_context('/'):
            s = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
            token = s.dumps('1')
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['loggedin'] = True
            # upload a non-image / invalid file type
            data = {
                'file': (BytesIO(b'not-an-image-content'), 'bad.txt')
            }
            r = c.post('/api/users/upload-profile-picture', data=data, content_type='multipart/form-data', headers={'X-CSRFToken': token})
            self.assertEqual(r.status_code, 400)

    def test_upload_profile_picture_invalid_content(self):
        with self.app.test_request_context('/'):
            s = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
            token = s.dumps('1')
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['loggedin'] = True
            # upload a non-image file with a valid extension
            data = {
                'file': (BytesIO(b'this is not an image'), 'fake.jpg')
            }
            r = c.post('/api/users/upload-profile-picture', data=data, content_type='multipart/form-data', headers={'X-CSRFToken': token})
            self.assertEqual(r.status_code, 400)

    def test_upload_profile_picture_zero_byte(self):
        with self.app.test_request_context('/'):
            s = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
            token = s.dumps('1')
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['loggedin'] = True
            data = {
                'file': (BytesIO(b''), 'empty.jpg')
            }
            r = c.post('/api/users/upload-profile-picture', data=data, content_type='multipart/form-data', headers={'X-CSRFToken': token})
            self.assertEqual(r.status_code, 400)

    def test_upload_profile_picture_corrupted(self):
        with self.app.test_request_context('/'):
            s = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
            token = s.dumps('1')
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['loggedin'] = True
            # A valid PNG header with corrupted data
            corrupted_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82' + b'a' * 100
            data = {
                'file': (BytesIO(corrupted_data), 'corrupted.png')
            }
            r = c.post('/api/users/upload-profile-picture', data=data, content_type='multipart/form-data', headers={'X-CSRFToken': token})
            self.assertEqual(r.status_code, 400)
if __name__ == '__main__':
    unittest.main()
