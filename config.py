import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '3b9c5f27a6d84c1e8f2a7b5d390e12f45a6b8c7d2e4f5a9b3c6d8e1f2a5b7c9'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = 'noreply@expenserfx.com'