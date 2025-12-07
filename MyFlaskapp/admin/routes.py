from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp
from MyFlaskapp.db import get_db_connection
import datetime
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('authenticated'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_user_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    year = str(datetime.datetime.now().year)
    query = "SELECT user_id FROM user_tb WHERE user_id LIKE %s ORDER BY user_id DESC LIMIT 1"
    cursor.execute(query, (year + '%',))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # result is like (user_id,)
        parts = result[0].split('-')
        if len(parts) > 1:
             last_num = int(parts[1])
             new_num = last_num + 1
        else:
             new_num = 1
    else:
        new_num = 1
    
    return f"{year}-{new_num:04d}"

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
@login_required
def users_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM user_tb')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin/users_list.html', users=users)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        user_id = generate_user_id()
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        birthdate = request.form['birthdate']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        address = request.form.get('address', '')
        user_type = request.form.get('user_type', 'user')

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO user_tb (user_id, firstname, lastname, birthdate, username, password, email, mobile_number, address, user_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(query, (user_id, firstname, lastname, birthdate, username, password, email, mobile_number, address, user_type))
            conn.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
            flash(f'Error adding user: {e}', 'danger')
        finally:
            conn.close()
            
    return render_template('admin/add_user.html')

@admin_bp.route('/update/<string:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        birthdate = request.form['birthdate']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        address = request.form.get('address', '')
        user_type = request.form.get('user_type', 'user')
        
        query = """UPDATE user_tb SET 
            firstname=%s, lastname=%s, birthdate=%s, username=%s, 
            password=%s, email=%s, mobile_number=%s, address=%s, user_type=%s
            WHERE user_id=%s"""
            
        try:
            cursor.execute(query, (firstname, lastname, birthdate, username, password, email, mobile_number, address, user_type, id))
            conn.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
             flash(f'Error updating user: {e}', 'danger')
        finally:
             conn.close()
    else:
        cursor.execute("SELECT * FROM user_tb WHERE user_id=%s", (id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('admin.users_list'))
            
        return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/delete', methods=['POST'])
@login_required
def delete_user():
    user_id = request.form.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_tb WHERE user_id=%s", (user_id,))
        conn.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin.users_list'))
