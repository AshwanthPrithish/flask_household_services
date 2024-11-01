from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from datetime import timedelta
import redis
import configparser
from celery import Celery
import logging 

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()
login_manager = LoginManager()
session_manager = Session()

app = Flask(__name__)

with open('../config.properties', 'r') as f:
    properties_content = '[DEFAULT]\n' + f.read()
    
config = configparser.ConfigParser()
config.read_string(properties_content)

app.config['SECRET_KEY'] = config.get('DEFAULT', 'secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.config['MAIL_SERVER'] = config.get('DEFAULT', 'mail.server')
app.config['MAIL_PORT'] = config.getint('DEFAULT', 'mail.port')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config.get('DEFAULT', 'mail.username')
app.config['MAIL_PASSWORD'] = str(config.get('DEFAULT', 'mail.password')[1:-1])
app.config['MAIL_DEFAULT_SENDER'] = config.get('DEFAULT', 'mail.default_sender')

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = True  
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
app.config['SESSION_USE_SIGNER'] = True  
app.config['SESSION_KEY_PREFIX'] = 'flask-session:'  
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0) 

logging.basicConfig(level=logging.INFO)

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/1'
app.config['CELERY_BROKER_TRANSPORT_OPTIONS'] = {'visibility_timeout': 3600}
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
celery.conf.result_backend = 'redis://localhost:6379/2' # type: ignore
celery.conf.timezone = 'Asia/Kolkata' # type: ignore
celery.conf.enable_utc = False

db.init_app(app)
mail.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
session_manager.init_app(app)
with app.app_context():
    db.create_all()
from flask_project import routes
from . import tasks
