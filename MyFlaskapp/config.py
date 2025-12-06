import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'  # Default XAMPP user
    MYSQL_PASSWORD = ''  # Default XAMPP password is empty
    MYSQL_DB = 'gemao_db'
    
    # Mail Config (Generic/Console)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT')) if os.environ.get('MAIL_PORT') else None
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True' if os.environ.get('MAIL_USE_TLS') else None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@gemao.com'
    
    # Session
    PERMANENT_SESSION_LIFETIME = 3600 # 1 hour
