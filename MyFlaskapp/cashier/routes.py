from flask import render_template, session, redirect, url_for, flash
from functools import wraps
from . import cashier_bp

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('authenticated'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@cashier_bp.route('/dashboard')
@login_required
def cashier_dashboard():
    if session.get('user_role') != 'cashier':
        flash('Access denied. This area is for cashiers only.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('cashier/cashier_dashboard.html')
