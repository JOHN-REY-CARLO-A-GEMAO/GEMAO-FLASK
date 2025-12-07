from flask import Blueprint, render_template, send_file, abort
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/categories')
def categories():
    return render_template('categories.html')

@main_bp.route('/categories/<int:category_id>')
def category_games(category_id):
    return render_template('category_games.html', category_id=category_id)

AUDIO_PATH = "c:\\Users\\Administrator\\Downloads\\GEMAO-FLASK (1)-20251205T044439Z-3-001\\GEMAO-FLASK\\Naruto Theme - The Raising Fighting Spirit.mp3"

@main_bp.route('/ambient')
def ambient():
    try:
        if not os.path.exists(AUDIO_PATH):
            abort(404)
        return send_file(AUDIO_PATH, mimetype='audio/mpeg', conditional=True)
    except Exception:
        abort(404)
