from flask import render_template, redirect, url_for, flash, request, session
from functools import wraps
from . import auth_bp
from MyFlaskapp.db import get_db_connection
from MyFlaskapp import mail
from flask_mail import Message
import random

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('authenticated'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            sql_query = "SELECT * FROM user_tb WHERE username = %s"
            cursor.execute(sql_query, (username,))
            user = cursor.fetchone()
            
            if user and user['password'] == password:
                # Generate OTP
                otp = str(random.randint(1000, 9999))
                
                # Store OTP in DB
                cursor.execute("INSERT INTO otp_tb (user_id, otp) VALUES (%s, %s)", (user['id'], otp)) # Using 'id' from user_tb, make sure it matches
                conn.commit()
                
                # Send Email with error handling
                try:
                    msg = Message('Your OTP', recipients=[user['email']])
                    msg.body = f'Your OTP is {otp}'
                    mail.send(msg)
                except Exception as e:
                    print(f"Email send failed during login for {username} ({user['email']}): {e}")
                    flash('Email delivery failed. Please try again later.', 'danger')
                    conn.close()
                    return render_template('auth/login.html')

                session['pre_2fa_user_id'] = user['user_id'] # Store user_id temporarily
                session['temp_user'] = user # Store user info temporarily
                
                conn.close()
                flash('OTP sent to your email.', 'info')
                return redirect(url_for('auth.verify'))
            else:
                conn.close()
                flash('Incorrect Credentials', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'pre_2fa_user_id' not in session:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        pin = request.form.get('pin')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get latest OTP for user
        # user_tb id is likely 'id' column, but user_id in session might be 'user_id' column (string).
        # We need to look up the DB ID based on pre_2fa_user_id (which looks like '573' or '221')
        # Let's verify what 'user' object structure is from 'login'.
        # login uses user['user_id'] for session.
        # otp_tb uses user_id which is FK to user_tb(id).
        # We need to find the user_tb(id) from session['pre_2fa_user_id'].
        
        user_info = session.get('temp_user')
        if not user_info:
             # Fallback if temp_user lost
             cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (session['pre_2fa_user_id'],))
             user_info = cursor.fetchone()

        cursor.execute("SELECT * FROM otp_tb WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_info['id'],))
        otp_record = cursor.fetchone()
        
        if otp_record and otp_record['otp'] == pin:
            # Login Success
            session.pop('pre_2fa_user_id', None)
            session.pop('temp_user', None)
            
            session.permanent = True
            session['user_id'] = user_info['user_id']
            session['user_name'] = f"{user_info['firstname']} {user_info['lastname']}"
            session['user_role'] = user_info['user_type']
            session['authenticated'] = True
            
            flash('You were successfully logged in', 'success')
            conn.close()
            
            if user_info['user_type'] == 'cashier':
                return redirect(url_for('cashier.cashier_dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            conn.close()
            flash('Invalid OTP', 'danger')
            
    return render_template('auth/verify.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', 
                         username=session.get('user_name'),
                         user_role=session.get('user_role'))
