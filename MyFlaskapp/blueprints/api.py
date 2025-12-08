from flask import Blueprint, request, jsonify, current_app, session
from flask_login import current_user
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import os
import uuid
import time
from collections import defaultdict
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from MyFlaskapp import categories

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
ALLOWED_FORMATS = {'JPEG', 'PNG', 'GIF'}
MIN_DIM = (100, 100)
MAX_DIM = (2000, 2000)
MAX_REQUESTS_PER_MINUTE = 5

_rate_limiter = defaultdict(list)

def _get_user_id():
    return getattr(current_user, 'id', None) or session.get('user_id')

def _rate_limit_check(key: str) -> bool:
    now = time.time()
    window_start = now - 60
    timestamps = _rate_limiter[key]
    _rate_limiter[key] = [t for t in timestamps if t >= window_start]
    if len(_rate_limiter[key]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    _rate_limiter[key].append(now)
    return True

def _validate_csrf() -> bool:
    token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
    if not token:
        return False
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        ident = s.loads(token, max_age=3600)
        uid = str(_get_user_id() or 'anon')
        return ident == uid
    except (BadSignature, SignatureExpired):
        return False

def _validate_image(file_storage):
    filename = secure_filename(file_storage.filename or '')
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, 'Unsupported file extension'
    try:
        file_storage.stream.seek(0)
        img = Image.open(file_storage.stream)
        img.verify()  # Verify that this is a valid image
        orig_fmt = (img.format or '').upper()
        if not orig_fmt or orig_fmt not in ALLOWED_FORMATS:
            return False, 'Unsupported image format'

        # Re-open the image after verification
        file_storage.stream.seek(0)
        img = Image.open(file_storage.stream)
        img = ImageOps.exif_transpose(img)
        w, h = img.size
        if w < MIN_DIM[0] or h < MIN_DIM[1]:
            return False, 'Image too small'
        if w > MAX_DIM[0] or h > MAX_DIM[1]:
            return False, 'Image too large'
        return True, {'image': img, 'ext': ext, 'format': orig_fmt}
    except Exception:
        return False, 'Invalid image file'

@api_bp.route('/users/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    uid = _get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    if not _validate_csrf():
        return jsonify({'error': 'CSRF validation failed'}), 400

    key = f'user:{uid}'
    if not _rate_limit_check(key):
        return jsonify({'error': 'Too many uploads'}), 429

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'error': 'Invalid file'}), 400

    ok, data = _validate_image(file)
    if not ok:
        return jsonify({'error': data}), 400

    img = data['image']
    ext = data['ext']

    folder = current_app.config.get('UPLOAD_FOLDER_PROFILE')
    os.makedirs(folder, exist_ok=True)

    unique_name = f"{uid}_{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(folder, unique_name)

    try:
        if ext in {'.jpg', '.jpeg'}:
            img.save(abs_path, format='JPEG', quality=88)
        elif ext == '.png':
            img.save(abs_path, format='PNG')
        elif ext == '.gif':
            img.save(abs_path, format='GIF')
        else:
            return jsonify({'error': 'Unsupported format'}), 400
    except Exception:
        return jsonify({'error': 'Failed to save image'}), 500

    try:
        import MyFlaskapp.db as db
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users SET profile_picture_path=%s, profile_picture_updated_at=NOW() WHERE id=%s
            """,
            (unique_name, uid)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        try:
            os.remove(abs_path)
        except Exception:
            pass
        return jsonify({'error': 'Database error'}), 500

    return jsonify({'success': True, 'filename': unique_name}), 200

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    all_categories = categories.get_all_categories()
    return jsonify(all_categories)

@api_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if categories.create_category(name, description):
        return jsonify({'success': True}), 201
    return jsonify({'error': 'Failed to create category'}), 500

@api_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = categories.get_category(category_id)
    if category:
        return jsonify(category)
    return jsonify({'error': 'Category not found'}), 404

@api_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if categories.update_category(category_id, name, description):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to update category'}), 500

@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    if categories.delete_category(category_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to delete category'}), 500

@api_bp.route('/categories/<int:category_id>/games', methods=['GET'])
def get_games_in_category(category_id):
    games_in_category = categories.get_games_in_category(category_id)
    return jsonify(games_in_category)

@api_bp.route('/games/<int:game_id>/categories', methods=['POST'])
def add_game_to_category(game_id):
    data = request.get_json()
    category_id = data.get('category_id')
    if not category_id:
        return jsonify({'error': 'Category ID is required'}), 400
    if categories.add_game_to_category(game_id, category_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to add game to category'}), 500

@api_bp.route('/games/<int:game_id>/categories/<int:category_id>', methods=['DELETE'])
def remove_game_from_category(game_id, category_id):
    if categories.remove_game_from_category(game_id, category_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to remove game from category'}), 500
