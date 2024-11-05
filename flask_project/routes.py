import secrets
import os
import re
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
   

@app.route("/view_customers")
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
            cache_data(cache_key, customers_serialized)  # Cache the serialized data
      return render_template("view_customers.html", title="View Customers", customers=customers)
   
   else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))


@app.route("/view_service_professionals")
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
            cache_data(cache_key, service_professionals_serialized)  # Cache the serialized
      return render_template("view_service_professionals.html", title="View Service Professionals", service_professionals=service_professionals)
   
   else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
   

@app.route("/view_service_requests")
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
      return render_template("view_service_requests.html", title="View Service Requests", service_requests=service_requests)
   
   else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))

@app.route("/register", methods=['POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == "customer":
            return jsonify({'redirect': url_for('home')}), 200
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
            return jsonify({'redirect': url_for('sp_dash')}), 200
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
        db.session.commit()
        
        redis_client.delete("view_customers_key")
        return jsonify({"message": "Account updated successfully"}), 200
    return jsonify({"error": "Bad Request"}), 400

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
        db.session.commit()
        
        redis_client.delete("view_service_professionals_key")
        return jsonify({"message": "Account updated successfully"}), 200
    return jsonify({"error": "Bad Request"}), 400


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
  return render_template("services.html", service_list=services_, title="Services")


@app.route("/service/new", methods=['GET', 'POST'])
@login_required
def new_service():
  if current_user.role != "admin":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role} acc", "danger")
    return redirect(url_for("home"))
  
  form = ServiceForm()
  if form.validate_on_submit():
      if len(Service.query.filter(func.lower(Service.name).ilike(f"%{form.name.data.lower()}%")).all()) > 0:
           flash('Service with that name already exists!', 'danger')
           return redirect(url_for('new_service'))
      service = Service(name=form.name.data, description=form.description.data,price=form.price.data) # type: ignore
      db.session.add(service)
      db.session.commit()

      redis_client.delete("services_key")
      flash('The Service has been created!', 'success')
      return redirect(url_for('services'))
  return render_template('create_service.html', title="New Service", form=form, legend='New Service')
  
@app.route("/service/<int:service_id>/update", methods=['GET', 'POST'])
@login_required
def update_service(service_id):
   if current_user.role != "admin":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
    return redirect(url_for("home"))
   else:
      form=UpdateServiceForm()
      service = Service.query.get_or_404(service_id)
      if form.validate_on_submit():
         service.name = form.name.data
         service.description = form.description.data
         service.price = form.price.data
         db.session.commit()
         redis_client.delete("services_key")
         flash('Service updated!', 'success')
         return redirect(url_for('services'))
      elif request.method == "GET":
         form.name.data = service.name
         form.description.data = service.description
         form.price.data = service.price  # type: ignore
      return render_template("update_service.html", form=form)

@app.route("/service/<int:service_id>/delete", methods=['POST'])
@login_required
def delete_service(service_id):
  if current_user.role != "admin":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
    return redirect(url_for("home"))
  
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
  flash('Service Deleted!', 'success')
  return redirect(url_for('sections'))
  
@app.route("/service/<int:service_id>")
@login_required
def service(service_id):
    cache_key = f"service:{service_id}"

    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        service = cached_data['service']
        service_name = service["name"]
        offered_by_professionals = cached_data['offered_by_professionals']
    else:
        service = Service.query.get_or_404(service_id)
        service_name = service.name
        
        offered_by_professionals = Service_Professional.query.filter_by(service_id=service_id).all()
        offered_by_professionals = [
            {
                "name": professional.username,
                "email": professional.email,
                "description": professional.description,
                "experience": professional.experience,
                "date_created": professional.date_created.isoformat(),
            }
            for professional in offered_by_professionals
        ]

        cache_data(cache_key, {'service': service.get_as_dict(), 'offered_by_professionals': offered_by_professionals}, timeout=300)  # Cache for 5 minutes
    return render_template('service.html', name=service_name, service=service, offered_by_professionals=[{
                "name": off["name"], # type: ignore
                "email": off["email"], # type: ignore
                "description": off["description"], # type: ignore
                "experience": off["experience"], # type: ignore
                "date_created": datetime.fromisoformat(off["date_created"]), # type: ignore
            } for off in offered_by_professionals])
 
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


@app.route("/service/<int:service_id>/request_service", methods=['GET', 'POST'])
@login_required
def request_service(service_id):
    if current_user.role != 'customer':
        flash("Access Denied! Only Customer can request Service", "danger")
        return redirect(url_for("home"))
    
    form = ServiceRequestForm()

    cache_key_requests_count = f"service_requests_count:{current_user.id}"
    cache_key_service_request = f"service_request:{current_user.id}:{service_id}"

    requests_count = get_cached_data(cache_key_requests_count)

    if requests_count is None:
        requests_count = len(Service_Request.query.filter(Service_Request.customer_id == current_user.id, func.lower(Service_Request.service_status) != "completed").all())
        cache_data(cache_key_requests_count, requests_count, timeout=300)

    service_request_exists = get_cached_data(cache_key_service_request)

    if service_request_exists is None:
        service_request_exists = len(Service_Request.query.filter(Service_Request.customer_id == current_user.id, Service_Request.service_id == service_id, Service_Request.service_status != "completed").all()) > 0
        cache_data(cache_key_service_request, service_request_exists, timeout=300)

    if requests_count >= 5:
        flash('You have already requested 5 services. Mark a service as complete to request this!', 'danger')
        return redirect(url_for('home'))
    
    if service_request_exists:
        flash('You have already requested this service!', 'danger')
        return redirect(url_for('home'))

    previous_request = Service_Request.query.filter_by(customer_id=current_user.id, service_id=service_id).first()
    if previous_request and previous_request.service_status == "requested":
        flash('You have already requested this service! Wait for admin approval of the previous request.', 'danger')
        return redirect(url_for('home'))

    if form.validate_on_submit():
        customer_id = current_user.id
        duration = form.request_duration.data
        td = duration_to_timedelta(duration)
        date_of_completion = form.date_of_request.data + td
        
        
        status = "requested"
        new_request = Service_Request(
                date_of_request=form.date_of_request.data, # type: ignore
                customer_id=customer_id, # type: ignore
                service_id=service_id, # type: ignore
                date_of_completion=date_of_completion, # type: ignore
                service_status=status # type: ignore
            )
        db.session.add(new_request)
        db.session.commit()

        cache_key = f"customer_requests_{current_user.id}"
        redis_client.delete(cache_key)
        cache_key = f"pending_requests"
        redis_client.delete(cache_key)
        redis_client.delete("view_service_requests_key")
        cache_data(cache_key_requests_count, requests_count + 1, timeout=300) 
        cache_data(cache_key_service_request, True, timeout=300)  

        flash('Service Requested Successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_service_request.html', title="Request this service", form=form)


@app.route("/complete-request/<int:request_id>", methods=['GET', 'POST'])
@login_required
def mark_request_as_complete(request_id):
   if current_user.role != "customer":
      flash(f"Access Denied! You do not have permission to view this page.", "danger")
      return redirect(url_for("home"))
   request = Service_Request.query.filter_by(id=request_id).first()

   if request.service_status != "assigned": # type: ignore
         flash(f"Service request is not yet assigned. Please wait to get it assigned first.", "danger")
         return redirect(url_for('home'))
      
   request.service_status = "completed" # type: ignore
   cache_key = f"past_services_{current_user.role}_{current_user.id}"
   redis_client.delete(cache_key)
   db.session.commit()
   cache_key = f"customer_requests_{current_user.id}"
   redis_client.delete(cache_key)
   redis_client.delete("view_service_requests_key")
   flash(f"Marked the service request as complete!", "success")
   return redirect(url_for('submit_remarks', request_id=request_id))


@app.route("/submit-remarks/<int:request_id>", methods=['GET', 'POST'])
@login_required
def submit_remarks(request_id):
   if current_user.role != "customer":
      flash(f"Access Denied! You do not have permission to view this page.", "danger")
      return redirect(url_for("home"))
   form = RemarkForm()
   if form.validate_on_submit():
      remark = Remarks(remarks=form.remark.data, service_request_id=request_id) # type: ignore
      db.session.add(remark)
      db.session.commit()
      cache_key = "cached_remarks"
      redis_client.delete(cache_key)
      flash(f"Remarks submitted successfully!", "success")
      return redirect(url_for('home'))
   return render_template('submit_remark.html', title='Submit Remarks', form=form)

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
      flash(f"Access Denied! You do not have permission to view this page.", "danger")
      return redirect(url_for("home"))
   request = Service_Request.query.filter_by(id=request_id).first()
   db.session.delete(request)
   db.session.commit()
   cache_key = f"customer_requests_{current_user.id}"
   redis_client.delete(cache_key)
   cache_key = "pending_requests"
   redis_client.delete(cache_key)
   redis_client.delete("view_service_requests_key")
   flash(f"Cancelled the service request!", "danger")
   return redirect(url_for('home'))


@app.route('/customer-requests')
@login_required
def customer_requests():
    if current_user.role != 'customer':
        flash(f"Access Denied! Only Customers can view requested services", "danger")
        return redirect(url_for("home"))

    cache_key = f"customer_requests_{current_user.id}"

    cached_data = get_cached_data(cache_key)

    if cached_data is not None:
        details = cached_data  
    else:
        service_requests = Service_Request.query.filter_by(customer_id=current_user.id).all()  # type: ignore
        details = []

        for service_request in service_requests:
            service_name = service_request.service.name
            customer_name = current_user.username
            service_id = service_request.service.id
            customer_id = current_user.id
            service_status = service_request.service_status
            date_of_request = service_request.date_of_request.strftime("%d-%m-%Y")
            date_of_completion = service_request.date_of_completion.strftime("%d-%m-%Y")

            if service_request.service_professional_id:
                service_professional_name = service_request.service_professional.username
                service_professional_id = service_request.service_professional_id
            else:
                service_professional_name = ""
                service_professional_id = ""

            details.append({
                'request_id': service_request.id,
                'service_name': service_name,
                'customer_name': customer_name,
                'service_professional_name': service_professional_name,
                'service_id': service_id,
                'customer_id': customer_id,
                'service_professional_id': service_professional_id,
                'service_status': service_status,
                'date_of_request': date_of_request,
                'date_of_completion': date_of_completion
            })  # type: ignore

        cache_data(cache_key, details, timeout=300)

    return render_template('customer_requests.html', requested_services=details, title='Requests')



@app.route('/pending-requests')
@login_required
def pending_requests():
    if current_user.role != "service_professional":
        flash(f"Access Denied! You do not have permission to view this page. {current_user.role}", "danger")
        return redirect(url_for("home"))

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

    return render_template('pending_requests.html', title="Pending Requests", requests=details)


@app.route('/export_csv')
def trigger_export():
   if current_user.role != "service_professional":
     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
     return redirect(url_for("home"))
   
   professional_id = current_user.id
   task = export_as_csv.apply_async(args=[professional_id]) # type: ignore
   flash(f"Export in progress", "success")
   return redirect(url_for("home"))

@app.route('/accept-request/<int:request_id>/<int:service_professional_id>', methods=['GET', 'POST'])
@login_required
def accept_request(request_id, service_professional_id):
   if current_user.role != "service_professional":
     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
     return redirect(url_for("home"))
   
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

   flash(f"Accepted Service", "success")
   return redirect(url_for("home"))

@app.route('/reject-request/<int:request_id>/<int:service_professional_id>', methods=['GET','POST'])
@login_required
def reject_request(request_id, service_professional_id):
   if current_user.role != "service_professional":
     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
     return redirect(url_for("home"))
   
   
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
   return redirect(url_for("home"))


@app.route('/past-services')
@login_required
def past_services():
    if current_user.role == 'admin':
        flash("Access Denied", "danger")
        return redirect(url_for("home"))

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

    return render_template("past_services.html", past_services=past_services)

   
def save_graph(filename, role, name):
   _, ext = os.path.splitext(filename)
   picture_fn = f"{role}_{name}" + ext
   picture_path = os.path.join(app.root_path, f'static/graphs', picture_fn)
   
   i = Image.open(filename)
   i.save(picture_path)
   
   return picture_fn

@app.route("/customer-graphs")
@login_required
def customer_graphs():
   if current_user.role != 'customer':
      flash("Access Denied! You do not have permission to view this page.", "danger")
      return redirect(url_for("home"))
   
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
   image_url = url_for('static', filename='graphs/' + image)

   service_requests = Service_Request.query.filter_by(customer_id=current_user.id).all()
   service_requests = [service.service_status for service in service_requests]
   value_counts = {}
   for value in service_requests:
      value_counts[value] = value_counts.get(value, 0) + 1

   # Pie chart
   plt.figure(figsize=(8, 8))
   plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140) # type: ignore
   plt.axis('equal')
   plt.title('Distribution of Service Status availed')
   picture_path = os.path.join(app.root_path, f'static/graphs/two.png')
   plt.savefig(picture_path)
   plt.close()

   image1 = save_graph(picture_path, 'customer', 'status')
   image_url1 = url_for('static', filename='graphs/' + image1)

   return render_template('graph.html', image=image_url,image1=image_url1, image2="",title="Graph")

 

@app.route("/sp-graphs")
@login_required
def sp_graphs():
   if current_user.role != 'service_professional':
      flash("Access Denied! You do not have permission to view this page.", "danger")
      return redirect(url_for("home"))
   
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
   image_url = url_for('static', filename='graphs/' + image)

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
   image_url1 = url_for('static', filename='graphs/' + image1)

   return render_template('graph.html', image=image_url,image1=image_url1, image2="",title="Graph")



@app.route("/admin-graphs")
@login_required
def admin_graphs():
   if current_user.role != 'admin':
      flash("Access Denied! You do not have permission to view this page.", "danger")
      return redirect(url_for("home"))
   
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
   image_url = url_for('static', filename='graphs/' + image)

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
   image_url1 = url_for('static', filename='graphs/' + image1)

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
   image_url2 = url_for('static', filename='graphs/' + image2)

   return render_template('graph.html', image=image_url,image1=image_url1, image2=image_url2,title="Graph")


@app.route("/test-mail")
@login_required
def test_mail():
    # Send a monthly activity report for a specific customer
    customer = current_user
    if customer:
        past_requests = Service_Request.query.filter_by(customer_id=customer.id, service_status="completed").all()
        html_content = render_template('monthly_report.html', requests=past_requests, customer=customer)
        msg = Message('Your Monthly Activity Report', recipients=["ashuarul2002@gmail.com"])
        msg.html = html_content
        mail.send(msg)
    return f"Report sent to {customer.email}"

# @app.route("/download/<int:book_id>")   
# @login_required
# def download_book(book_id):
#    if current_user.role == "librarian" or len(BookIssue.query.filter_by(book_id=book_id,student_id=current_user.id).all()) <= 0:
#     flash("Access Denied! You do not have permission to view this page.", "danger")
#     return redirect(url_for("home"))
#    else:
#       lang_dict = {'hindi': 'Noto Sans Devanagari', 'tamil': 'Noto Serif Tamil', 'telugu': 'Noto Sans Telugu', 'malayalam': 'Noto Sans Malayalam', 'kannada': 'Noto Sans Kannada', 'english':''}
#       book=Book.query.filter_by(id=book_id).first()
#       lang = book.lang.lower()

#       if lang not in lang_dict.keys():
#          flash(f'Cannot download {lang} language book!', 'danger')
#          return redirect(url_for("home"))
      
#       rendered = render_template('download_content.html', book=book, font_lang=lang_dict[lang])
      
#       config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
#       pdf = pdfkit.from_string(rendered, configuration=config)

#       response = make_response(pdf)
#       response.headers['Content-Type'] = 'application/pdf'
#       response.headers['Content-Disposition'] = 'inline;filename=output.pdf'

#       return response
   


# # API Endpoints

# # get books
# @app.route("/api/books", methods=['GET'])
# def api_get_books():
#    books = Book.query.all()
#    books = [{
#    'id' : book.id,
#    'author' : book.author,
#    'lang' : book.lang,
#    'content' : book.content,
#    'librarian_id' : book.librarian_id,
#    'genre_id' : book.genre_id} for book in books]
#    return jsonify(books)

# # post books
# @app.route("/api/books/add", methods=['DELETE'])
# @token_required
# def api_add_book(user_from_token):
#    data = request.json
#    if user_from_token.role != 'librarian':
#       return ({'message': 'Invalid credentials'}), 401
   
#    else:
#       if len(Book.query.filter_by(title=data['title']).all()) > 0:
#          return ({'message': 'Book already exists'}), 401
#       year = datetime.strptime(data['release_year'], "%Y")
#       book = Book(title=data['title'],author=data['author'],content=data['content'], lang=data['lang'], rating=data['rating'],release_year=year,librarian_id=user_from_token.id,genre_id=data['genre_id'])
#       with app.app_context():
#          db.session.add(book)
#          db.session.commit()
#       return jsonify({"message": "Successfully added the book"}), 200


# #put books
# @app.route("/api/books/update", methods=["PUT"])
# @token_required
# def api_update_book(user_from_token):
#     if user_from_token.role != "librarian":
#       return ({'message': 'Invalid credentials'}), 401
  
#     data = request.json
#     title = data['title']
#     id = Book.query.filter_by(title=title).first().id
#     book = Book.query.get_or_404(id)
#     if 'author' in data: book.author=data['author']
#     if 'content' in data: book.content=data['content']
#     if 'lang' in data: book.lang=data['lang']
#     if 'rating' in data: book.rating=data['rating']
#     if 'release_year' in data: book.release_year=data['release_year']
#     db.session.commit()
    
#     return jsonify({"message": "Successfully updated the book"}), 200



# #delete books
# @app.route("/api/books/delete", methods=['POST'])
# @token_required
# def api_delete_book(user_from_token):
#    data = request.json
#    if user_from_token.role != 'librarian':
#       return ({'message': 'Invalid credentials'}), 401
   
#    else:
#       if len(Book.query.filter_by(title=data['title']).all()) < 0:
#          return ({'message': 'Book does not exist'}), 401
#       id = Book.query.filter_by(title=data['title']).first().id
#       with app.app_context():
#          book = Book.query.get_or_404(id)
         
#          feedbacks = FeedBack.query.filter_by(book_id=id).all()
#          for feedback in feedbacks:
#                db.session.delete(feedback)
#                db.session.commit()
         
#          db.session.delete(book)
#          db.session.commit()
#       return jsonify({"message": "Successfully deleted the book"}), 200

# # student login api
# @app.route("/api/login", methods=['POST'])
# def api_login():
#   auth = request.json

#   if auth and 'email' in auth and 'password' in auth and 'role' in auth:
#      email = auth['email']
#      password = auth['password']

#      student = Student.query.filter_by(email=email).first()
#      if(bcrypt.check_password_hash(student.password, password)):
#             token = jwt.encode({'email': email, 'role': 'student'}, app.config['SECRET_KEY'])
#             return jsonify({'token': token}), 200
 
#   return jsonify({'message': 'Invalid credentials'}), 401


# # librarian login api
# @app.route("/api/sp-login", methods=['POST'])
# def api_login_librarian():
#   auth = request.json

#   if auth and 'email' in auth and 'password' in auth:
#      email = auth['email']
#      password = auth['password']

#      librarian = Librarian.query.filter_by(email=email).first()
#      if(bcrypt.check_password_hash(librarian.password, password)):
#             token = jwt.encode({'email': email, 'role': 'librarian'}, app.config['SECRET_KEY'])
#             return jsonify({'token': token}), 200
 
#   return jsonify({'message': 'Invalid credentials'}), 401


# #get student books
# @app.route("/api/student-books", methods=["GET"])
# @token_required
# def api_student_books(user_from_token):
#    book_issues = BookIssue.query.filter_by(student_id=user_from_token.id).all()
#    books = [Book.query.filter_by(id=book_issue.book_id).first() for book_issue in book_issues]
#    books = [{
#    'id' : book.id,
#    'author' : book.author,
#    'lang' : book.lang,
#    'content' : book.content,
#    'librarian_id' : book.librarian_id,
#    'genre_id' : book.genre_id} for book in books]
#    return jsonify(books)
   