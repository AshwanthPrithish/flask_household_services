from flask_project import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import class_mapper

@login_manager.user_loader
def load_user(user_id):
    if(int(user_id) == -1):
        return Admin.query.get(int(user_id))
    if int(user_id) >= 10000:
        return Service_Professional.query.get(int(user_id))
    else:
        return Customer.query.get(int(user_id))
    
class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = "admin"

    def get_as_dict(self):
        mapper = class_mapper(self.__class__)
        """Convert the Customer instance to a dictionary."""
        return {column.name: getattr(self, column.name) for column in mapper.columns if not column.name == "password"}


class Customer(db.Model, UserMixin):
    __tablename__ = 'customer'  
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(400), nullable=False)
    contact = db.Column(db.String(15), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    role = "customer"

    # Relationship to Service_Request
    service_requests = db.relationship('Service_Request', back_populates='customer', lazy=True)

    def __repr__(self):
        return f"Customer('{self.username}', '{self.email}', '{self.image_file}')"
    
    def get_as_dict(self):
        mapper = class_mapper(self.__class__)
        """Convert the Customer instance to a dictionary."""
        return {column.name: getattr(self, column.name) for column in mapper.columns if not column.name == "password"}



class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Relationship to Service_Request
    service_requests = db.relationship('Service_Request', back_populates='service', lazy=True)

    def __repr__(self):
        return f"Service('{self.name}', '{self.description}')"
    
    def get_as_dict(self):
        mapper = class_mapper(self.__class__)
        """Convert the Customer instance to a dictionary."""
        return {column.name: getattr(self, column.name) for column in mapper.columns if not column.name == "password"}



class Service_Professional(db.Model, UserMixin):
    __tablename__ = 'service_professional'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(400), nullable=False)
    experience = db.Column(db.String(400), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # Foreign key to relate to Service
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service_requests = db.relationship('Service_Request', back_populates='service_professional', lazy=True)
    role = "service_professional"

    def __repr__(self):
        return f"Service Professional('{self.username}', '{self.email}')"
    
    def get_as_dict(self):
        mapper = class_mapper(self.__class__)
        """Convert the Customer instance to a dictionary."""
        return {column.name: getattr(self, column.name) for column in mapper.columns if not column.name == "password"}



class Service_Request(db.Model):
    __tablename__ = 'service_request'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_of_request = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=False)
    service_status = db.Column(db.String(100), nullable=False)

    # Foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)  # Foreign key for Service

    # Relationships
    customer = db.relationship('Customer', back_populates='service_requests')
    service_professional = db.relationship('Service_Professional', back_populates='service_requests')
    service = db.relationship('Service', back_populates='service_requests')

    def __repr__(self):
        return f"Service_Request('{self.date_of_request}', '{self.date_of_completion}')"
    
    def get_as_dict(self):
        mapper = class_mapper(self.__class__)
        """Convert the Customer instance to a dictionary."""
        return {column.name: getattr(self, column.name) for column in mapper.columns if not column.name == "password"}



class Remarks(db.Model):
    __tablename__ = 'remarks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    remarks = db.Column(db.String(100), nullable=False)

    # Foreign key
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)

    def __repr__(self):
        return f"Remark('{self.service_request_id}', '{self.remarks}')"
    
    def get_as_dict(self):
        mapper = class_mapper(self.__class__)
        """Convert the Customer instance to a dictionary."""
        return {column.name: getattr(self, column.name) for column in mapper.columns if not column.name == "password"}

