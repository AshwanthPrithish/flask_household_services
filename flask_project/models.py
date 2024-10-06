from flask_project import db, login_manager
from datetime import datetime
import datetime as dt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    user = None
    
    if (int(user_id) >= 10000):
        user = Service_Professional.query.filter_by(id=int(user_id)).first()
    else:
        user = Customer.query.filter_by(id=int(user_id)).first()
    
    return user
class Customer(db.Model, UserMixin):
    __tablename__ = 'customer'  # Explicitly defining the table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(400), unique=False, nullable=False)
    contact = db.Column(db.String(15), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    service_request = db.relationship('Service_Request', backref='customer', lazy=True)
    role = "customer"

    def __repr__(self):
        return f"Customer('{self.username}', '{self.email}', '{self.image_file}')"

class Service_Professional(db.Model, UserMixin):
    __tablename__ = 'service_professional'  # Explicitly defining the table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    description = db.Column(db.String(400), unique=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    experience = db.Column(db.String(400), unique=False, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    service = db.relationship('Service', backref='service_professional', lazy=True)
    service_request = db.relationship('Service_Request', backref='service_professional', lazy=True)
    role = "service_professional"

    def __repr__(self):
        return f"Service Professional('{self.username}', '{self.email}', '{self.image_file}')"

class Service(db.Model):
    __tablename__ = 'service'  # Explicitly defining the table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    service_requests = db.relationship('Service_Request', backref='service', lazy=True)

    def __repr__(self):
        return f"Service('{self.name}', '{self.description}')"

class Service_Request(db.Model):
    __tablename__ = 'service_request'  # Explicitly defining the table name
    id = db.Column(db.Integer, primary_key=True)
    date_of_request = db.Column(db.DateTime, nullable=False, default=datetime.now(dt.timezone.utc))
    date_of_completion = db.Column(db.DateTime, nullable=False)
    service_status = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=False)
    remark_id = db.Column(db.Integer, db.ForeignKey('remarks.id'), nullable=False)

    def __repr__(self):
        return f"Service_Request('{self.date_of_request}', '{self.date_of_completion}')"

class Remarks(db.Model):
    __tablename__ = 'remarks'  # Explicitly defining the table name
    id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.String(100), nullable=False)
    service_request = db.relationship('Service_Request', backref='remark', lazy=True)

    def __repr__(self):
        return f"Remark('{self.service_request}', '{self.remarks}')"
