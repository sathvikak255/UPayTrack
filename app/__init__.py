from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os
from threading import Thread

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    login_manager.login_view = 'main.login'
    
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            from app.routes import send_monthly_report
            email_thread = Thread(target=send_monthly_report)
            email_thread.daemon = True
            email_thread.start()
    
    return app