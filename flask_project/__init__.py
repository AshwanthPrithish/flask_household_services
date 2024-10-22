from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from datetime import timedelta
import redis


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cf5502128e89ac7e636ca2dd6c913212'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = True  
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
app.config['SESSION_USE_SIGNER'] = True  
app.config['SESSION_KEY_PREFIX'] = 'flask-session:'  
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)  

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
Session(app)

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
bcrypt = Bcrypt()
login_manager = LoginManager(app)

from flask_project import routes