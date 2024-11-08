import secrets
import os
import re
from sqlite3 import IntegrityError
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import jwt
import json

from datetime import datetime, timedelta
from PIL import Image
from flask import render_template,flash, redirect, session, url_for, request, jsonify,send_from_directory, current_app
from flask_project import db, bcrypt, mail, app, celery
from flask_project.forms import AdminLoginForm, RegistrationForm, LoginForm, RemarkForm, SPLoginForm, SPRegistrationForm, SearchServiceForm, SearchServiceProfessionalForm, ServiceForm, ServiceRequestForm, UpdateCustomerAccount, UpdateSPAccount, UpdateServiceForm
from flask_project.models import Admin, Customer, Service_Professional, Service, Service_Request, Remarks
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func, not_
from flask_project.auth_middleware import token_required
from flask_mail import Message
from flask_project.redis_client import redis_client
from flask_project.tasks import export_as_csv
from flask_wtf.csrf import CSRFProtect, generate_csrf

def cache_data(key, data, timeout=300):
    """Store data in Redis with a timeout."""
    redis_client.setex(key, timeout, json.dumps(data))

def get_cached_data(key):
    """Retrieve cached data from Redis."""
    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data) # type: ignore
    return None

csrf = CSRFProtect(app)

with app.app_context():
  db.create_all()

@app.route("/auth_status", methods=["GET"])
def auth_status():
    
    csrf_token = generate_csrf()
    if current_user.is_authenticated:
        if current_user.role == 'customer':
            customer = Customer.query.filter_by(id=current_user.id).first()
            user_info = {
                  'isAuthenticated': 'True',
                  'role': current_user.role,
                  'username':   customer.username, # type: ignore
                  'email': customer.email, # type: ignore
                  'csrf':csrf_token,
                  'id': current_user.id
            }
        elif current_user.role == 'service_professional':
            service_professional = Service_Professional.query.filter_by(id=current_user.id).first()
            user_info = {
                  'isAuthenticated': 'True',
                  'role': current_user.role,
                  'username':   service_professional.username, # type: ignore
                  'email': service_professional.email, # type: ignore
                  'csrf':csrf_token,
                  'id': current_user.id
            }
        else: 
            admin = Admin.query.filter_by(id=current_user.id).first()
            user_info = {
                  'isAuthenticated': 'True',
                  'role': current_user.role,
                  'username':   admin.username, # type: ignore
                  'email': admin.email, # type: ignore
                  'csrf':csrf_token,
                  'id': current_user.id
            }
    else:
        user_info = {'is_authenticated': False, "role": '', 'csrf': csrf_token, 'id':'null'}
    
    return jsonify(user_info)


@app.route("/")
@app.route("/home")
def home():
  return render_template("home.html", title="Home")

@app.route("/about-us")
def about_us():
  return render_template("about_us.html", title="About us")

@app.route("/contact")
def contact():
  return render_template("contact.html", title="Contact")

@app.route("/fetch-services")
def fetch_services():
  services = Service.query.all()
  return jsonify([service.get_as_dict() for service in services]), 200


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    if current_user.is_authenticated:
      logout_user()
      return jsonify({"message": "Successfully logged out"}), 200
    else:
       return jsonify({"message": "Unexpected error"}), 200


@app.route("/admin-login", methods=['GET', 'POST'])
def admin_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided', 'success': False}), 400

        data['remember'] = True if data['remember'] == 'true' else False
        form = AdminLoginForm(data=data)

        if current_user.is_authenticated:
            if current_user.role == "admin":
                return jsonify({'message': 'Already logged in as admin', 'success': True}), 200
            else:
                return jsonify({'message': 'Access Denied! You do not have permission to view this page.', 'success': False}), 403
        if form.validate_on_submit():
            admin = Admin.query.filter_by(email=form.email.data).first()
            if admin and bcrypt.check_password_hash(admin.password, form.password.data):
                token = jwt.encode({'email': form.email.data, 'role': 'admin'}, app.config['SECRET_KEY'])
                login_user(admin, remember=data['remember'])

                session.permanent = True
                session['user_id'] = admin.id
                session['role'] = 'admin'

                return jsonify({
                    'token': token,
                    'success': True,
                    'isAuthenticated': True,
                    'role': current_user.role,
                    'username': admin.username,
                    'email': admin.email
                }), 200
            else:
                return jsonify({'message': 'Invalid credentials', 'success': False}), 401

        else:
            errors = {field: form.errors.get(field, []) for field in form.errors}
            return jsonify({'errors': errors, 'success': False}), 400

    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500


@app.route("/admin-dash", methods=['GET'])
@login_required
def admin_dash():
    if current_user.role == "admin":
        return jsonify(username=current_user.username) 
    else:
        return jsonify(error="Access Denied!"), 403
   

@app.route("/view-customers")
@login_required
def view_customers():
   if current_user.role == "admin":
      cache_key = "view_customers_key"
      cached_customers = get_cached_data(cache_key)
      if cached_customers:
            customers = cached_customers
      else:
            customers = Customer.query.filter(not_(Customer.username.ilike('%dummy%'))).all()
            customers_serialized = [c.get_as_dict() for c in customers]
            cache_data(cache_key, customers_serialized)  
            cached_customers =  get_cached_data(cache_key)
      return jsonify(cached_customers), 200
   
   else:
      return jsonify(error="Access Denied!"), 403


@app.route("/view-service-professionals")
@login_required
def view_service_professionals():
   if current_user.role == "admin":
      cache_key = "view_service_professionals_key"
      cached_sps = get_cached_data(cache_key)
      if cached_sps:
            service_professionals = [
               {**sp, 'date_created': datetime.fromisoformat(sp['date_created'])}
               for sp in cached_sps
            ]
      else:
            service_professionals = Service_Professional.query.filter(not_(Service_Professional.username.ilike('%dummy%'))).all()
            service_professionals_serialized = [ {**sp.get_as_dict(), 'date_created': sp.date_created.isoformat()}  for sp in service_professionals]
            cache_data(cache_key, service_professionals_serialized)  
            cached_sps =  get_cached_data(cache_key)
      return jsonify(cached_sps), 200
   
   else:
       return jsonify(error="Access Denied!"), 403
   

@app.route("/view-service-requests")
@login_required
def view_service_requests():
   if current_user.role == "admin":
      cache_key = "view_service_requests_key"
      cached_service_requests = get_cached_data(cache_key)
      if cached_service_requests:
            service_requests = [
            {
               **sr,
               'date_of_request': datetime.fromisoformat(sr['date_of_request']),
               'date_of_completion': datetime.fromisoformat(sr['date_of_completion'])
            }
            for sr in cached_service_requests
         ]
      else:
            service_requests = Service_Request.query.all()
            service_requests_serialized = [
               {
                  **sr.get_as_dict(),
                  'date_of_request': sr.date_of_request.isoformat() if isinstance(sr.date_of_request, datetime) else sr.date_of_request,
                  'date_of_completion': sr.date_of_completion.isoformat() if isinstance(sr.date_of_completion, datetime) else sr.date_of_completion,
                  'service_name': sr.service.name if sr.service.name else '',
                  'service_professional_name': sr.service_professional.username if sr.service_professional else '',
                  'customer_name': sr.customer.username if sr.customer else '',

               }
               for sr in service_requests
            ]

            cache_data(cache_key, service_requests_serialized)  # Cache the serialized
            service_requests =  [
                    {
                        **sr,
                        'date_of_request': datetime.fromisoformat(sr['date_of_request']),
                        'date_of_completion': datetime.fromisoformat(sr['date_of_completion'])
                    }
                for sr in get_cached_data(cache_key) # type: ignore
            ]
            cached_service_requests = service_requests
      return jsonify(cached_service_requests), 200
   
   else:
       return jsonify(error="Access Denied!"), 403

@app.route("/register", methods=['POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == "customer":
            return jsonify({'message': "Already registed!"}), 200
        else:
            return jsonify({'message': "Access Denied! You do not have permission to view this page."}), 403

    data = request.get_json()
    form = RegistrationForm(data=data)
    
    if form.validate_on_submit():
        # Check for uniqueness
        existing_user = Customer.query.filter(
            (Customer.username == form.username.data) |
            (Customer.email == form.email.data) |
            (Customer.contact == form.contact.data)
        ).first()

        if existing_user:
            if existing_user.username == form.username.data:
                return jsonify({'message': 'Username already exists.'}), 400
            if existing_user.email == form.email.data:
                return jsonify({'message': 'Email already exists.'}), 400
            if existing_user.contact == form.contact.data:
                return jsonify({'message': 'Contact number already exists.'}), 400
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        customer = Customer(
            username=form.username.data, # type: ignore
            email=form.email.data, # type: ignore
            address=form.address.data, # type: ignore
            contact=form.contact.data, # type: ignore
            password=hashed_password # type: ignore
        )

        try:
            with app.app_context():
                db.session.add(customer)
                db.session.commit()

            return jsonify({'message': f'Account created for {form.username.data}!'}), 201
        except Exception as e:
            return jsonify({'message': str(e)}), 500
        
    errors = {field: form.errors.get(field, []) for field in form.errors}
    return jsonify({'errors': errors}), 400

@app.route("/login", methods=['GET', 'POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided', 'success': False}), 400

        data['remember'] = True if data['remember'] == 'true' else False
        form = LoginForm(data=data)

        if current_user.is_authenticated:
            if current_user.role == "customer":
                return jsonify({'message': 'Already logged in as customer', 'success': True}), 200
            else:
                return jsonify({'message': 'Access Denied! You do not have permission to view this page.', 'success': False}), 403

        if form.validate_on_submit():
            customer = Customer.query.filter_by(email=form.email.data).first()
            if customer and bcrypt.check_password_hash(customer.password, form.password.data):
                token = jwt.encode({'email': form.email.data, 'role': 'customer'}, app.config['SECRET_KEY'])
                login_user(customer, remember=data['remember'])

                session.permanent = True
                session['user_id'] = customer.id
                session['role'] = 'customer'

                return jsonify({
                    'token': token,
                    'success': True,
                    'isAuthenticated': True,
                    'role': current_user.role,
                    'username': customer.username,
                    'email': customer.email
                }), 200
            else:
                return jsonify({'message': 'Invalid credentials', 'success': False}), 401

        else:
            errors = {field: form.errors.get(field, []) for field in form.errors}
            return jsonify({'errors': errors, 'success': False}), 400

    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500

@app.route("/customer-dash", methods=['GET'])
@login_required
def customer_dash():
    if current_user.role == "customer":
        return jsonify(username=current_user.username) 
    else:
        return jsonify(error="Access Denied!"), 403
   

@app.route("/sp-register", methods=['POST'])
def sp_register():
    if current_user.is_authenticated:
        if current_user.role == "service_professional":
             return jsonify({"error": "Unauthorized"}), 403
        else:
            return jsonify({'message': "Access Denied! You do not have permission to view this page."}), 403

    data = request.get_json()
    form = SPRegistrationForm(data=data)

    if form.validate_on_submit():
        existing_user = Service_Professional.query.filter(
            (Service_Professional.username == form.username.data) |
            (Service_Professional.email == form.email.data)
        ).first()

        if existing_user:
            if existing_user.username == form.username.data:
                return jsonify({'message': 'Username already exists.'}), 400
            if existing_user.email == form.email.data:
                return jsonify({'message': 'Email already exists.'}), 400
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        service = Service.query.filter_by(id=int(form.service.data)).first()
        if not service:
            return jsonify({'message': 'Selected service is invalid.'}), 400

        service_professional = Service_Professional(
            username=form.username.data, # type: ignore
            email=form.email.data, # type: ignore
            password=hashed_password, # type: ignore
            description=form.description.data, # type: ignore
            experience=form.experience.data, # type: ignore
            service_id=service.id# type: ignore
        )

        try:
            db.session.add(service_professional)
            db.session.commit()
            return jsonify({'message': f'Account created for Service Professional {form.username.data}!'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500

    errors = {field: form.errors.get(field, []) for field in form.errors}
    return jsonify({'errors': errors}), 400


@app.route("/sp-login", methods=['GET', 'POST'])
def sp_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided', 'success': False}), 400

        data['remember'] = True if data['remember'] == 'true' else False
        form = SPLoginForm(data=data)

        if current_user.is_authenticated:
            if current_user.role == "service_professional":
                return jsonify({'message': 'Already logged in as service professional', 'success': True}), 200
            else:
                return jsonify({'message': 'Access Denied! You do not have permission to view this page.', 'success': False}), 403

        if form.validate_on_submit():
            service_professional = Service_Professional.query.filter_by(email=form.email.data).first()
            if service_professional and bcrypt.check_password_hash(service_professional.password, form.password.data):
                token = jwt.encode({'email': form.email.data, 'role': 'service_professional'}, app.config['SECRET_KEY'])
                login_user(service_professional, remember=data['remember'])

                # Cache session details
                session.permanent = True
                session['user_id'] = service_professional.id
                session['role'] = 'service_professional'

                return jsonify({
                    'token': token,
                    'success': True,
                    'isAuthenticated': True,
                    'role': current_user.role,
                    'username': service_professional.username,
                    'email': service_professional.email
                }), 200
            else:
                return jsonify({'message': 'Invalid credentials', 'success': False}), 401

        else:
            errors = {field: form.errors.get(field, []) for field in form.errors}
            return jsonify({'errors': errors, 'success': False}), 400

    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500

   

@app.route("/sp-dash", methods=['GET'])
@login_required
def sp_dash():
    if current_user.role == "service_professional":
        return jsonify(username=current_user.username) 
    else:
        return jsonify(error="Access Denied!"), 403

@app.route("/search-results-service", methods=["POST"])
@login_required
def search_results_service():
    query = request.get_json().get('service')
    cache_key = f"search_results_service:{query.lower()}"
    
    cached_services = get_cached_data(cache_key)
    if cached_services:
        services = cached_services  
    else:
        services = Service.query.filter(func.lower(Service.name).ilike(f"%{query.lower()}%")).all()
        services = [{'id': service.id, 'name': service.name, 'price': service.price, 'description': service.description} for service in services]
        services.sort(key=lambda x: x.get('id'), reverse=False) # type: ignore
        
        cache_data(cache_key, services, timeout=300)  

    if len(services) <= 0:
        return jsonify([]), 200

    return jsonify(services)


@app.route("/search-results-service-professional", methods=["POST"])
@login_required
def search_results_service_professional():
    query = request.get_json().get('service_professional')
    cache_key = f"search_results_service_professional:{query.lower()}"
    cached_service_professionals = get_cached_data(cache_key)
    if cached_service_professionals:
        service_professionals = cached_service_professionals  
    else:
        service_professionals = Service_Professional.query.filter(func.lower(Service_Professional.username).ilike(f"%{query.lower()}%")).all()
        service_professionals = [{'id': service_professional.id, 'name': service_professional.username, 'email': service_professional.email, 'description': service_professional.description, 'experience': service_professional.experience, 'date_created': datetime.isoformat(service_professional.date_created)} for service_professional in service_professionals]
        service_professionals.sort(key=lambda x: x.get('id'), reverse=False) # type: ignore
        
        cache_data(cache_key, service_professionals, timeout=300)

    if len(service_professionals) <= 0:
        return jsonify([]), 200

    return jsonify(service_professionals)



@app.route('/media/<path:filename>')
def serve_static(filename):
    return send_from_directory(current_app.static_folder, filename) # type: ignore


def save_picture(form_picture, role):
   random_hex = secrets.token_hex(8)
   _, ext = os.path.splitext(form_picture.filename)
   picture_fn = random_hex + ext
   picture_path = os.path.join(app.root_path, f'static/profile_pics/{role}', picture_fn)
   
   output_size = (125, 125)
   i = Image.open(form_picture)
   i.thumbnail(output_size)
   i.save(picture_path)
   
   return picture_fn

@app.route("/customer-account", methods=['GET', 'POST'])
@login_required
def customer_account():
    if current_user.role != 'customer':
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'GET':
        return jsonify({
            "username": current_user.username,
            "email": current_user.email,
            "address": current_user.address,
            "contact": current_user.contact,
            "profilePictureUrl": f'profile_pics/{current_user.role}_pics/{current_user.image_file}'
        }), 200

    elif request.method == 'POST':
        data = request.form
        if 'picture' in request.files:
            picture_file = save_picture(request.files['picture'], 'customer_pics')
            current_user.image_file = picture_file
        current_user.username = data.get('username', current_user.username)
        current_user.email = data.get('email', current_user.email)
        current_user.address = data.get('address', current_user.address)
        current_user.contact = data.get('contact', current_user.contact)
        try:
            db.session.commit()
            redis_client.delete("view_customers_key")
            return jsonify({"message": "Account updated successfully"}), 200
        except Exception:
            db.session.rollback()  
            return jsonify({"message": "Integrity Error: Email or username might already be in use."}), 400
    return jsonify({"message": "Bad Request"}), 400

@app.route("/sp-account", methods=['GET', 'POST'])
@login_required
def sp_account():
    if current_user.role != 'service_professional':
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'GET':
        service = Service.query.get_or_404(current_user.service_id)
        service = service.get_as_dict()
        return jsonify({
            "username": current_user.username,
            "email": current_user.email,
            "description": current_user.description,
            "experience": current_user.experience,
            "service": service,
            "profilePictureUrl": f'profile_pics/{current_user.role}_pics/{current_user.image_file}'
        }), 200

    elif request.method == 'POST':
        data = request.form
        if 'picture' in request.files:
            picture_file = save_picture(request.files['picture'], 'service_professional_pics')
            current_user.image_file = picture_file
        current_user.username = data.get('username', current_user.username)
        current_user.email = data.get('email', current_user.email)
        current_user.description = data.get('description', current_user.description)
        current_user.experience = data.get('experience', current_user.experience)
        current_user.service_id = data.get('service_id', current_user.service_id)
        try:
            db.session.commit()
            redis_client.delete("view_service_professionals_key")
            return jsonify({"message": "Account updated successfully"}), 200
        except Exception:
            db.session.rollback()
            return jsonify({"message": "Integrity Error: Email or username might already be in use."}), 400
    return jsonify({"message": "Bad Request"}), 400


@app.route("/services")
@login_required
def services():
  cache_key = "services_key"
  cached_services = get_cached_data(cache_key)
  if cached_services:
    services_ = cached_services
  else:
     services_ = [service.get_as_dict() for service in Service.query.all()]
     services_.sort(key=lambda x: x.get('id'), reverse=False) # type: ignore
     cache_data(cache_key, services_, timeout=300)
  return jsonify(services_), 200

@app.route("/service/new", methods=['POST'])
@login_required
def new_service():
    if current_user.role != "admin":
        return jsonify({"message": "Access Denied! You do not have permission to view this page."}), 400

    form = ServiceForm()
    if form.validate_on_submit():
        if Service.query.filter(func.lower(Service.name) == form.name.data.lower()).first():
            return jsonify({"message": "Service with that name already exists!"}), 400
        
        service = Service(
            name=form.name.data,  # type: ignore
            description=form.description.data, # type: ignore# type: ignore
            price=form.price.data # type: ignore
        )
        db.session.add(service)
        db.session.commit()
        
        redis_client.delete("services_key")
        
        return jsonify({"message": "The Service has been created!"}), 201
    
    errors = {field: error for field, error in form.errors.items()}
    return jsonify({"errors": errors}), 400

  
@app.route("/service/<int:service_id>/update", methods=['GET', 'POST'])
@login_required
def update_service(service_id):
    if current_user.role != "admin":
       return jsonify({"message": "Access Denied! You do not have permission to view this page."}), 400
   
    service = Service.query.get_or_404(service_id)
    data = request.get_json()
    form = UpdateServiceForm(data=data)

    if form.validate():
        try:
            service.name = form.name.data # type: ignore
            service.description = form.description.data # type: ignore
            service.price = form.price.data # type: ignore
            db.session.commit()
            redis_client.delete("services_key")
            return jsonify({"message": "Service updated!"}), 200
        except Exception:
            db.session.rollback()
            return jsonify({"errors": {"name": ["A service with that name already exists."]}}), 400
    errors = {field: error for field, error in form.errors.items()}
    return jsonify({"errors": errors}), 400

@app.route("/service/<int:service_id>/delete", methods=['POST'])
@login_required
def delete_service(service_id):
  if current_user.role != "admin":
    return jsonify({"message": "Access Denied! You do not have permission to view this page."}), 400
  
  service = Service.query.get_or_404(service_id)
  service_requests = Service_Request.query.filter_by(service_id=service_id).all()
  for service_request in service_requests:
        db.session.delete(service_request)
        db.session.commit()
  service_professionals = Service_Professional.query.filter_by(service_id=service_id).all()
  for service_professional in service_professionals:
        db.session.delete(service_professional)
        db.session.commit()
  redis_client.delete("services_key")
  db.session.delete(service)
  db.session.commit()
  return jsonify({'message': "Deleted the service"}), 200
  
@app.route("/service/<int:service_id>")
@login_required
def service(service_id):
    cache_key = f"service:{service_id}"

    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return jsonify(cached_data), 200
    else:
        service = Service.query.get_or_404(service_id)
        
        offered_by_professionals = Service_Professional.query.filter_by(service_id=service_id).all()
        offered_by_professionals = [
            {
                "name": professional.username,
                "email": professional.email,
                "description": professional.description,
                "experience": professional.experience,
                "date_created": professional.date_created.isoformat(),
            }
            for professional in offered_by_professionals if "dummy" not in professional.username
        ]

        cache_data(cache_key, {'service': service.get_as_dict(), 'offered_by_professionals': offered_by_professionals}, timeout=300)  # Cache for 5 minutes
        cached_data = get_cached_data(cache_key)
        return jsonify(cached_data), 200
 
def duration_to_timedelta(st):
    s = 0
    pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)')
    matches = pattern.findall(st)
    result = [[int(match[0]), match[1]] for match in matches]
    for i, j in result:
       if j == 'minutes' or j == 'minute':
          s += (i * 60)
       elif j == 'hours' or j == 'hour':
          s += (i * 60 * 60)
       elif j == 'days' or j == 'day':
          s += (i * 60 * 60 * 24)
       elif j == 'weeks' or j == 'week':
          s += (i * 60 * 60 * 24 * 7)
    return timedelta(seconds=s)


@app.route("/service/<int:service_id>/request_service", methods=['POST'])
@login_required
def request_service(service_id):
    if current_user.role != 'customer':
        return jsonify({"flash": "Access Denied! Only customers can request services."}), 403

    data = request.get_json()
    date_of_request = datetime.strptime(data.get('date_of_request'), "%d-%m-%Y")
    request_duration = data.get('request_duration')

    errors = {}
    if not date_of_request:
        errors['date_of_request'] = 'Date of request is required.'
    if not request_duration:
        errors['request_duration'] = 'Request duration is required.'

    if errors:
        return jsonify({"errors": errors}), 400

    cache_key_requests_count = f"service_requests_count:{current_user.id}"
    cache_key_service_request = f"service_request:{current_user.id}:{service_id}"
    requests_count = get_cached_data(cache_key_requests_count)

    if requests_count is None:
        requests_count = len(Service_Request.query.filter(
            Service_Request.customer_id == current_user.id,
            func.lower(Service_Request.service_status) != "completed"
        ).all())
        cache_data(cache_key_requests_count, requests_count, timeout=300)

    service_request_exists = get_cached_data(cache_key_service_request)

    if service_request_exists is None:
        service_request_exists = Service_Request.query.filter(
            Service_Request.customer_id == current_user.id,
            Service_Request.service_id == service_id,
            Service_Request.service_status != "completed"
        ).count() > 0
        cache_data(cache_key_service_request, service_request_exists, timeout=300)

    if requests_count >= 5:
        return jsonify({"message": "You have already requested 5 services. Complete a service to request a new one."}), 400
    
    if service_request_exists:
        return jsonify({"message": "You have already requested this service."}), 400

    previous_request = Service_Request.query.filter_by(
        customer_id=current_user.id,
        service_id=service_id
    ).first()
    if previous_request and previous_request.service_status == "requested":
        return jsonify({"message": "You have already requested this service! Wait for admin approval of the previous request."}), 400

    duration_timedelta = duration_to_timedelta(request_duration)
    date_of_completion = date_of_request + duration_timedelta

    new_request = Service_Request(
        date_of_request=date_of_request, # type: ignore
        customer_id=current_user.id,  # type: ignore
        service_id=service_id,  # type: ignore
        date_of_completion=date_of_completion,  # type: ignore
        service_status="requested"  # type: ignore
    )
    db.session.add(new_request)
    db.session.commit()

    redis_client.delete(f"customer_requests_{current_user.id}")
    redis_client.delete("view_service_requests_key")
    cache_data(cache_key_requests_count, requests_count + 1, timeout=300)
    cache_data(cache_key_service_request, True, timeout=300)

    return jsonify({"message": "Service requested successfully!"}), 200

@app.route("/complete-request/<int:request_id>", methods=['GET', 'POST'])
@login_required
def mark_request_as_complete(request_id):
   if current_user.role != "customer":
      return jsonify({"error": "Access Denied! Only Customers can view requested services"}), 403
   request = Service_Request.query.filter_by(id=request_id).first()

   if request.service_status != "assigned": # type: ignore
        return jsonify({"error": "Service request is not yet assigned. Please wait to get it assigned first."}), 403
      
   request.service_status = "completed" # type: ignore
   cache_key = f"past_services_{current_user.role}_{current_user.id}"
   redis_client.delete(cache_key)
   db.session.commit()
   cache_key = f"customer_requests_{current_user.id}"
   redis_client.delete(cache_key)
   redis_client.delete("view_service_requests_key")
   return jsonify({"message": "Marked Service as complete"}), 200


@app.route("/submit-remarks/<int:request_id>", methods=['GET', 'POST'])
@login_required
def submit_remarks(request_id):
    if current_user.role != "customer":
      return jsonify({"message": "Access Denied! You do not have permission to view this page."}), 403
    remark_text = request.get_json().get("remark")
    if not remark_text:
        return jsonify({"errors": {"remark": ["Remark cannot be empty."]}}), 400

    remark = Remarks(remarks=remark_text, service_request_id=request_id) # type: ignore
    db.session.add(remark)
    db.session.commit()
    cache_key = "cached_remarks"
    redis_client.delete(cache_key)

    return jsonify({"message": "Remarks submitted successfully!"}), 200

@app.route("/remarks")
def remarks():
    cache_key_remarks = "cached_remarks"
    
    cached_remarks = get_cached_data(cache_key_remarks)
    
    if cached_remarks is not None:
        f = cached_remarks  
    else:
        remarks = Remarks.query.all()
        f = []
        for remark in remarks:
            service_request = Service_Request.query.filter_by(id=remark.service_request_id).first_or_404()
            service_name = Service.query.filter_by(id=service_request.service_id).first().name  # type: ignore
            service_professional_name = Service_Professional.query.filter_by(id=service_request.service_professional_id).first().username  # type: ignore
            customer_name = Customer.query.filter_by(id=service_request.customer_id).first().username  # type: ignore
            
            f.append({
                'service_name': service_name,
                'service_professional_name': service_professional_name,
                'customer_name': customer_name,
                'remark': remark.remarks
            })
        cache_data(cache_key_remarks, f, timeout=300)
    return jsonify(f)


@app.route("/cancel/<int:request_id>", methods=['GET', 'POST'])
@login_required
def cancel_request(request_id):
   if current_user.role != "customer":
      return jsonify({"error": "Access Denied! Only Customers can view requested services"}), 403
   request = Service_Request.query.filter_by(id=request_id).first()
   db.session.delete(request)
   db.session.commit()
   cache_key = f"customer_requests_{current_user.id}"
   redis_client.delete(cache_key)
   cache_key = "pending_requests"
   redis_client.delete(cache_key)
   redis_client.delete("view_service_requests_key")
   return jsonify({"message": "Cancelled request"}), 200


@app.route('/customer-requests')
@login_required
def customer_requests():
    if current_user.role != 'customer':
        return jsonify({"error": "Access Denied! Only Customers can view requested services"}), 403

    cache_key = f"customer_requests_{current_user.id}"
    cached_data = get_cached_data(cache_key)

    if cached_data is not None:
        details = cached_data  
    else:
        service_requests = Service_Request.query.filter_by(customer_id=current_user.id).all()
        details = []

        for service_request in service_requests:
            details.append({
                'request_id': service_request.id,
                'service_name': service_request.service.name,
                'customer_id': current_user.id,
                'customer_name': current_user.username,
                'service_professional_name': service_request.service_professional.username if service_request.service_professional_id else "",
                'service_professional_id': service_request.service_professional_id if service_request.service_professional_id else "",
                'service_id': service_request.service.id,
                'service_status': service_request.service_status,
                'date_of_request': service_request.date_of_request.strftime("%d-%m-%Y"),
                'date_of_completion': service_request.date_of_completion.strftime("%d-%m-%Y")
            })
        cache_data(cache_key, details, timeout=300)

    return jsonify({'services':details}), 200


@app.route('/pending-requests')
@login_required
def pending_requests():
    if current_user.role != "service_professional":
         return jsonify({"error": "Access Denied! Only Service Professionals can view requested services"}), 403

    cache_key = "pending_requests"

    cached_data = get_cached_data(cache_key)

    if cached_data is not None:
        details = cached_data  
    else:
        requests = Service_Request.query.filter_by(service_status="requested").all()
        details = []

        for service_request in requests:
            service_name = service_request.service.name
            customer_name = service_request.customer.username
            service_id = service_request.service.id
            customer_id = service_request.customer_id
            service_status = service_request.service_status
            date_of_request = service_request.date_of_request.strftime("%d-%m-%Y")
            date_of_completion = service_request.date_of_completion.strftime("%d-%m-%Y")

            details.append({
                'request_id': service_request.id,
                'service_name': service_name,
                'customer_name': customer_name,
                'service_id': service_id,
                'customer_id': customer_id,
                'service_status': service_status,
                'date_of_request': date_of_request,
                'date_of_completion': date_of_completion
            })  # type: ignore

        cache_data(cache_key, details, timeout=300)

    return jsonify({'pending_requests': details}), 200


@app.route('/export_csv')
def trigger_export():
   if current_user.role != "service_professional":
    return jsonify({"error": "Access Denied! Only Service Professionals can accept requested services"}), 403
   
   professional_id = current_user.id
   task = export_as_csv.apply_async(args=[professional_id]) # type: ignore
   return jsonify({"message": "Export Triggered"}), 200

@app.route('/accept-request/<int:request_id>/<int:service_professional_id>', methods=['GET', 'POST'])
@login_required
def accept_request(request_id, service_professional_id):
   if current_user.role != "service_professional":
      return jsonify({"error": "Access Denied! Only Service Professionals can accept requested services"}), 403
   
   request = Service_Request.query.filter_by(id=request_id).first()
   request.service_professional_id = service_professional_id # type: ignore
   request.service_professional = Service_Professional.query.filter_by(id=service_professional_id).first()  # type: ignore
   request.service_status = "assigned" # type: ignore

   cache_key = f"customer_requests_{request.customer.id}" # type: ignore
   redis_client.delete(cache_key)
      
   db.session.commit()
      

   cache_key = "pending_requests"
   redis_client.delete(cache_key)
   redis_client.delete("view_service_requests_key")

   return jsonify({"message": "Accepted Service Request!"}), 200

@app.route('/reject-request/<int:request_id>/<int:service_professional_id>', methods=['GET','POST'])
@login_required
def reject_request(request_id, service_professional_id):
   if current_user.role != "service_professional":
     return jsonify({"error": "Access Denied! Only Service Professionals can accept requested services"}), 403
   
   
   request = Service_Request.query.filter_by(id=request_id).first()
   request.service_professional_id = service_professional_id # type: ignore
   request.service_professional = Service_Professional.query.filter_by(id=service_professional_id).first()  # type: ignore
   request.service_status = "rejected" # type: ignore

   cache_key = f"customer_requests_{request.customer.id}" # type: ignore
   redis_client.delete(cache_key)
      
   db.session.commit()
   cache_key = "pending_requests"
   redis_client.delete(cache_key)
   redis_client.delete("view_service_requests_key")
   flash(f"Rejected Service", "success")
   return jsonify({"message": "Rejected Service Request!"}), 200


@app.route('/past-services')
@login_required
def past_services():
    if current_user.role == 'admin':
        return jsonify({"message": "Access Denied! You do not have permission to view this page."}), 403

    cache_key = f"past_services_{current_user.role}_{current_user.id}"

    cached_data = get_cached_data(cache_key)

    if cached_data is not None:
        past_services = [
            {
               **sr,
               'date_of_request': datetime.fromisoformat(sr['date_of_request']),
               'date_of_completion': datetime.fromisoformat(sr['date_of_completion'])
            }
            for sr in cached_data
         ]
    else:
        if current_user.role == "customer":
            past_services = Service_Request.query.filter_by(customer_id=current_user.id, service_status="completed").all()
            past_requests_serialized = [
               {
                  **sr.get_as_dict(),
                  'date_of_request': sr.date_of_request.isoformat() if isinstance(sr.date_of_request, datetime) else sr.date_of_request,
                  'date_of_completion': sr.date_of_completion.isoformat() if isinstance(sr.date_of_completion, datetime) else sr.date_of_completion,
                  'service_name': sr.service.name if sr.service.name else '',
                  'service_professional_name': sr.service_professional.username if sr.service_professional else '',
                  'customer_name': sr.customer.username if sr.customer else '',

               }
               for sr in past_services
            ]
        else:
            past_services = Service_Request.query.filter_by(service_professional_id=current_user.id, service_status="completed").all()
            past_requests_serialized = [
               {
                  **sr.get_as_dict(),
                  'date_of_request': sr.date_of_request.isoformat() if isinstance(sr.date_of_request, datetime) else sr.date_of_request,
                  'date_of_completion': sr.date_of_completion.isoformat() if isinstance(sr.date_of_completion, datetime) else sr.date_of_completion,
                  'service_name': sr.service.name if sr.service.name else '',
                  'service_professional_name': sr.service_professional.username if sr.service_professional else '',
                  'customer_name': sr.customer.username if sr.customer else '',

               }
               for sr in past_services
            ]

        cache_data(cache_key, past_requests_serialized, timeout=300)
        past_services =  [
                    {
                        **sr,
                        'date_of_request': datetime.fromisoformat(sr['date_of_request']),
                        'date_of_completion': datetime.fromisoformat(sr['date_of_completion'])
                    }
                for sr in get_cached_data(cache_key) # type: ignore
            ]
    return jsonify(past_services), 200

   
def save_graph(filename, role, name):
   _, ext = os.path.splitext(filename)
   picture_fn = f"{role}_{name}" + ext
   picture_path = os.path.join(app.root_path, f'static/graphs/{role}_graphs/', picture_fn)
   
   i = Image.open(filename)
   i.save(picture_path)
   
   return picture_fn

@app.route("/customer-graphs")
@login_required
def customer_graphs():
   if current_user.role != 'customer':
       return jsonify(error="Access Denied!"), 403

   service_requests = Service_Request.query.filter_by(customer_id=current_user.id).all()
   service_requests = [service.service.name for service in service_requests]
   value_counts = {}
   for value in service_requests:
      value_counts[value] = value_counts.get(value, 0) + 1

   # Pie chart
   plt.figure(figsize=(8, 8))
   plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140) # type: ignore
   plt.axis('equal')
   plt.title('Distribution of Service Names availed')
   picture_path = os.path.join(app.root_path, f'static/graphs/one.png')
   plt.savefig(picture_path)
   plt.close()

   image = save_graph(picture_path, 'customer', 'requests')
   image = f'graphs/{current_user.role}_graphs/' + image

   service_requests = Service_Request.query.filter_by(customer_id=current_user.id).all()
   service_requests = [service.service_status for service in service_requests]
   value_counts  = {}
   for value in service_requests:
      value_counts[value] = value_counts.get(value, 0) + 1

   # Pie chart
   plt.figure(figsize=(8, 8))
   plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140) # type: ignore
   plt.axis('equal')
   plt.title('Distribution of Service Status')
   picture_path = os.path.join(app.root_path, f'static/graphs/two.png')
   plt.savefig(picture_path)
   plt.close()

   image1 = save_graph(picture_path, 'customer', 'status')
   image1 = f'graphs/{current_user.role}_graphs/' + image1

   return jsonify({'one':image,'two': image1,'three':""}), 200

 

@app.route("/sp-graphs")
@login_required
def sp_graphs():
   if current_user.role != 'service_professional':
     return jsonify(error="Access Denied!"), 403
   
   service_requests = Service_Request.query.filter_by(service_professional_id=current_user.id).all()
   service_requests = [service.customer.username for service in service_requests]
   value_counts = {}
   for value in service_requests:
      value_counts[value] = value_counts.get(value, 0) + 1

   # Pie chart
   plt.figure(figsize=(8, 8))
   plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140) # type: ignore
   plt.axis('equal')
   plt.title('Distribution of Customer Names involved')
   picture_path = os.path.join(app.root_path, f'static/graphs/one.png')
   plt.savefig(picture_path)
   plt.close()

   image = save_graph(picture_path, 'service_professional', 'customers')
   image = f'graphs/{current_user.role}_graphs/' + image

   service_requests = Service_Request.query.filter_by(service_professional_id=current_user.id).all()
   service_requests = [service.service_status for service in service_requests]
   value_counts = {}
   for value in service_requests:
      value_counts[value] = value_counts.get(value, 0) + 1

   # Pie chart
   plt.figure(figsize=(8, 8))
   plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140) # type: ignore
   plt.axis('equal')
   plt.title('Distribution of Service Status offered')
   picture_path = os.path.join(app.root_path, f'static/graphs/two.png')
   plt.savefig(picture_path)
   plt.close()

   image1 = save_graph(picture_path, 'service_professional', 'status')
   image1 = f'graphs/{current_user.role}_graphs/' + image1

   return jsonify({'one':image,'two': image1,'three':""}), 200



@app.route("/admin-graphs")
@login_required
def admin_graphs():
   if current_user.role != 'admin':
       return jsonify({"error": "Unauthorized"}), 403
   
   service_requests = Service_Request.query.filter_by().all()
   service_requests = [service.customer.username for service in service_requests]
   value_counts = {}
   for value in service_requests:
      value_counts[value] = value_counts.get(value, 0) + 1

   # Pie chart
   plt.figure(figsize=(8, 8))
   plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140) # type: ignore
   plt.axis('equal')
   plt.title('Distribution of Customer Names involved')
   picture_path = os.path.join(app.root_path, f'static/graphs/one.png')
   plt.savefig(picture_path)
   plt.close()

   image = save_graph(picture_path, 'admin', 'customers')
   image = f'graphs/{current_user.role}_graphs/' + image

   service_requests = Service_Request.query.filter_by().all()
   service_requests = [service.service_status for service in service_requests]
   value_counts = {}
   for value in service_requests:
      value_counts[value] = value_counts.get(value, 0) + 1

   # Pie chart
   plt.figure(figsize=(8, 8))
   plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140) # type: ignore
   plt.axis('equal')
   plt.title('Distribution of Service Status offered')
   picture_path = os.path.join(app.root_path, f'static/graphs/two.png')
   plt.savefig(picture_path)
   plt.close()

   image1 = save_graph(picture_path, 'admin', 'status')
   image1 = f'graphs/{current_user.role}_graphs/' + image1

   service_requests = Service_Request.query.filter_by().all()
   service_requests = [service.service_professional.username for service in service_requests if service.service_professional != None]
   value_counts = {}
   for value in service_requests:
      value_counts[value] = value_counts.get(value, 0) + 1

   # Pie chart
   plt.figure(figsize=(8, 8))
   plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140) # type: ignore
   plt.axis('equal')
   plt.title('Distribution of Service Professional Names involved')
   picture_path = os.path.join(app.root_path, f'static/graphs/three.png')
   plt.savefig(picture_path)
   plt.close()

   image2 = save_graph(picture_path, 'admin', 'service_professionals')
   image2 = f'graphs/{current_user.role}_graphs/' + image2

   return jsonify({'one':image,'two': image1,'three':image2}), 200
