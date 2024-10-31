# from flask import Flask, session
# from flask_mail import Mail
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from flask_session import Session
# from datetime import timedelta
# import redis
# import configparser

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'cf5502128e89ac7e636ca2dd6c913212'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# with open('../config.properties', 'r') as f:
#     properties_content = '[DEFAULT]\n' + f.read()

# config = configparser.ConfigParser()
# config.read_string(properties_content)

# app.config['MAIL_SERVER'] = config.get('DEFAULT', 'mail.server')
# app.config['MAIL_PORT'] = config.getint('DEFAULT', 'mail.port')
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = config.get('DEFAULT', 'mail.username')
# app.config['MAIL_PASSWORD'] = str(config.get('DEFAULT', 'mail.password')[1:-1])
# app.config['MAIL_DEFAULT_SENDER'] = config.get('DEFAULT', 'mail.default_sender')

# # Session configuration for redis
# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = True  
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
# app.config['SESSION_USE_SIGNER'] = True  
# app.config['SESSION_KEY_PREFIX'] = 'flask-session:'  
# app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)  

# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
# Session(app)
# mail = Mail(app)

# db = SQLAlchemy(app)
# with app.app_context():
#     db.create_all()
# bcrypt = Bcrypt()
# login_manager = LoginManager(app)

# from flask_project import routes
# from flask_project.tasks import send_daily_reminders, send_monthly_report  # Import tasks

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from datetime import timedelta
import redis
import configparser

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()
login_manager = LoginManager()
session_manager = Session()

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'cf5502128e89ac7e636ca2dd6c913212'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    # Load properties from config file
    with open('../config.properties', 'r') as f:
        properties_content = '[DEFAULT]\n' + f.read()
    
    config = configparser.ConfigParser()
    config.read_string(properties_content)

    # Mail configuration
    app.config['MAIL_SERVER'] = config.get('DEFAULT', 'mail.server')
    app.config['MAIL_PORT'] = config.getint('DEFAULT', 'mail.port')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = config.get('DEFAULT', 'mail.username')
    app.config['MAIL_PASSWORD'] = str(config.get('DEFAULT', 'mail.password')[1:-1])
    app.config['MAIL_DEFAULT_SENDER'] = config.get('DEFAULT', 'mail.default_sender')

    # Redis session configuration
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = True  
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
    app.config['SESSION_USE_SIGNER'] = True  
    app.config['SESSION_KEY_PREFIX'] = 'flask-session:'  
    app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)  

    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    session_manager.init_app(app)

    with app.app_context():
        db.create_all()
    from flask_project import routes
    from .routes import bp as main_bp
    app.register_blueprint(main_bp, url_prefix="")

    return app
