from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cf5502128e89ac7e636ca2dd6c913212'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
bcrypt = Bcrypt()
login_manager = LoginManager(app)

from flask_project import routes