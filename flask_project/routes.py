import secrets
import os
import re
import pdfkit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import jwt

from datetime import datetime, timedelta
from PIL import Image
from flask import render_template,flash, redirect, url_for, request, make_response, jsonify
from flask_project import app, db, bcrypt
from flask_project.forms import AdminLoginForm, RegistrationForm, LoginForm, RemarkForm, SPLoginForm, SPRegistrationForm, SearchServiceForm, SearchServiceProfessionalForm, ServiceForm, ServiceRequestForm, UpdateCustomerAccount, UpdateSPAccount
from flask_project.models import Admin, Customer, Service_Professional, Service, Service_Request, Remarks
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
from flask_project.auth_middleware import token_required

with app.app_context():
  db.create_all()

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


@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for('home'))


@app.route("/admin-login", methods=['GET', 'POST'])
def admin_login():
  form = AdminLoginForm()
  if current_user.is_authenticated:
    if current_user.role == "admin":
       return redirect(url_for('home'))
    else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
  if form.validate_on_submit():
    admin = Admin.query.filter_by(email=form.email.data).first()
    if admin and bcrypt.check_password_hash(admin.password, form.password.data):
      login_user(admin, remember=form.remember.data)
      flash(f'Your admin login was success!', 'success')
      return redirect(url_for('admin_dash'))
    else:
      flash('Login unsuccessful, please check email, and password', 'danger')
      
  return render_template("admin_login.html", title="Login", form=form)

@app.route("/admin-dash", methods=['GET', 'POST'])
@login_required
def admin_dash():
   if current_user.role == "admin":
      form = SearchServiceForm()
      if form.validate_on_submit():
        service = form.service.data
        return redirect(url_for('search_results_service', query=service))
      
      form1 = SearchServiceProfessionalForm()
      if form1.validate_on_submit():
          service_professional = form1.service_professional.data
          return redirect(url_for('search_results_service_professional', query=service_professional))
      return render_template("admin_dashboard.html", title="Admin Dashboard")

   else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))


@app.route("/register", methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    if current_user.role == "customer":
       return redirect(url_for('home'))
    else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
  form = RegistrationForm()
  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    customer = Customer(username=form.username.data, email=form.email.data, address=form.address.data, contact=form.contact.data,password=hashed_password) # type: ignore
    with app.app_context():
      db.session.add(customer)
      db.session.commit()

    flash(f'Your customer Account has been created!', 'success')
    return redirect(url_for("login"))
  return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if current_user.is_authenticated:
    if current_user.role == "customer":
       return redirect(url_for('home'))
    else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
  if form.validate_on_submit():
    customer = Customer.query.filter_by(email=form.email.data).first()
    if customer and bcrypt.check_password_hash(customer.password, form.password.data):
      login_user(customer, remember=form.remember.data)
      flash(f'Your customer login was success!', 'success')
      return redirect(url_for('customer_dash'))
    else:
      flash('Login unsuccessful, please check email, and password', 'danger')
      
  return render_template("login.html", title="Login", form=form)


@app.route("/customer-dash", methods=['GET', 'POST'])
@login_required
def customer_dash():
   if current_user.role == "customer":
      form = SearchServiceForm()
      if form.validate_on_submit():
        service = form.service.data
        return redirect(url_for('search_results_service', query=service))
      
      form1 = SearchServiceProfessionalForm()
      if form1.validate_on_submit():
          service_professional = form1.service_professional.data
          return redirect(url_for('search_results_service_professional', query=service_professional))
      return render_template("customer_dashboard.html", title="Customer Dashboard", form=form, form1=form1)

   else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
   

@app.route("/sp_register",methods=['GET', 'POST'])
def sp_register():
    if current_user.is_authenticated:
        if current_user.role == "service_professional":
          return redirect(url_for('sp_dash'))
        else:
          flash("Access Denied! You do not have permission to view this page.", "danger")
          return redirect(url_for("home"))
    form = SPRegistrationForm()
    services = Service.query.all()
    form.service.choices = [service.name for service in services]
    if form.validate_on_submit():
       hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
       service_professional = Service_Professional(username=form.username.data, email=form.email.data, password=hashed_password, description=form.description.data, experience=form.experience.data, service_id=Service.query.filter_by(name=form.service.data).first().id) # type: ignore
       with app.app_context():
         db.session.add(service_professional)
         db.session.commit()
       flash(f'Account Created for Service professional {form.username.data}!', 'success')
       return redirect(url_for("sp_login"))
    return render_template("sp_register.html", title="Admin Register", form=form, services=services)


@app.route("/sp-login", methods=['GET', 'POST'])
def sp_login():
  form = SPLoginForm()
  if current_user.is_authenticated:
    if current_user.role == "service_professional":
       return redirect(url_for('sp_dash'))
    else:
       flash(f"Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
  
  if form.validate_on_submit():
    service_professional = Service_Professional.query.filter_by(email=form.email.data).first()
    if service_professional and bcrypt.check_password_hash(service_professional.password, form.password.data):
      login_user(service_professional, remember=form.remember.data)
      flash('Login successful', 'success')
      return redirect(url_for('sp_dash'))
    else:
      flash('Login unsuccessful, please check email, and password', 'danger')
  return render_template("sp_login.html", title="Admin Login", form=form)
   

@app.route("/sp_dash")
def sp_dash():
    if current_user.role == "service_professional":
      form = SearchServiceForm()
      if form.validate_on_submit():
        service = form.service.data
        return redirect(url_for('search_results_service', query=service))
      
      form1 = SearchServiceProfessionalForm()
      if form1.validate_on_submit():
          service_professional = form1.service_professional.data
          return redirect(url_for('search_results_service_professional', query=service_professional))
      return render_template("sp_dashboard.html", title="Service Professional Dashboard", form=form, form1=form1)

    else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))


@app.route("/search-results-service/<query>")
@login_required
def search_results_service(query):
   services = Service.query.filter(func.lower(Service.name).ilike(f"%{query.lower()}%")).all()
   services = [{'id':service.id,'name':service.name, 'price':service.price,'description': service.description }  for service in services]
   services.sort(key = lambda x: x.get('id'), reverse=False) # type: ignore
   if len(services) <= 0:
      flash(f'No services found for the query {query}!', 'danger')
      return redirect(url_for('home'))
   return render_template('search_results_service.html', services=services, title='Search by Service Name')


@app.route("/search-results-service-professional/<query>")
@login_required
def search_results_service_professional(query):
   service_professionals = Service_Professional.query.filter(func.lower(Service_Professional.username).ilike(f"%{query.lower()}%")).all()
   service_professionals = [{'id':service_professional.id,'name':service_professional.username, 'email':service_professional.email,'description': service_professional.description, 'experience':service_professional.experience, 'date_created':service_professional.date_created }  for service_professional in service_professionals]
   service_professionals.sort(key = lambda x: x.get('id'), reverse=False) # type: ignore
   if len(service_professionals) <= 0:
      flash(f'No service professionals found for the query {query}!', 'danger')
      return redirect(url_for('home'))
   return render_template('search_results_service_professional.html', service_professionals=service_professionals, title='Search by Service Professional Name')


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

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
  image_file = None
  if current_user.role == "customer":
        form = UpdateCustomerAccount()
        if form.validate_on_submit():
            if form.picture.data:
               picture_file = save_picture(form.picture.data, 'student_pics')
               with app.app_context():
                current_user.image_file = picture_file
                db.session.commit()
            with app.app_context():
              current_user.username = form.username.data
              current_user.email = form.email.data
              current_user.address = form.address.data
              current_user.contact = form.contact.data
              db.session.commit()
            flash('Your Account has been updated!', category='success')
            return redirect(url_for('account'))
        elif request.method == "GET":
           form.username.data = current_user.username
           form.email.data = current_user.email
           form.address.data = current_user.address
           form.contact.data = current_user.contact
        image_file = url_for('static', filename='profile_pics/student_pics/' + current_user.image_file)
        return render_template("customer_account.html", title="Student Account", image_file=image_file, form=form)
  
  elif current_user.role == "service_professional":
        form = UpdateSPAccount()
        form.service.choices = [service.name for service in Service.query.all()]
        if form.validate_on_submit():
            if form.picture.data:
               picture_file = save_picture(form.picture.data, 'admin_pics')
               with app.app_context():
                current_user.image_file = picture_file
                db.session.commit()
            with app.app_context():
              current_user.username = form.username.data
              current_user.email = form.email.data
              current_user.description = form.description.data
              current_user.experience = form.experience.data
              current_user.service_id = Service.query.filter_by(name=form.service.data).first().id # type: ignore
              db.session.commit()
            flash('Your Account has been updated!', category='success')
            return redirect(url_for('account'))
        elif request.method == "GET":
           form.username.data = current_user.username
           form.email.data = current_user.email
           form.description.data = current_user.description
           form.experience.data = current_user.experience
           selected_service = Service.query.filter_by(id=current_user.service_id).first().name # type: ignore
           if selected_service:
                form.service.data = selected_service

        image_file = url_for('static', filename='profile_pics/admin_pics/' + current_user.image_file)
        return render_template("sp_account.html", title="Librarian Account", image_file=image_file, form=form)
  
  else:
        flash(f"Access Denied! You do not have permission to view this page.{current_user.role} acc", "danger")
        return redirect(url_for("home"))


@app.route("/services")
@login_required
def services():
  with app.app_context():
     services_ = [i for i in Service.query.all()]
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
      with app.app_context():
         db.session.add(service)
         db.session.commit()
         flash('The Service has been created!', 'success')
      return redirect(url_for('services'))
  return render_template('create_service.html', title="New Service", form=form, legend='New Service')
  


@app.route("/service/<int:service_id>/delete", methods=['POST'])
@login_required
def delete_service(service_id):
  if current_user.role != "admin":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
    return redirect(url_for("home"))
  
  with app.app_context():
     service = Service.query.get_or_404(service_id)
     service_requests = Service_Request.query.filter_by(service_id=service_id).all()
     for service_request in service_requests:
        db.session.delete(service_request)
        db.session.commit()
     service_professionals = Service_Professional.query.filter_by(service_id=service_id).all()
     for service_professional in service_professionals:
        db.session.delete(service_professional)
        db.session.commit()
     db.session.delete(service)
     db.session.commit()
     flash('Service Deleted!', 'success')
     return redirect(url_for('sections'))
  
@app.route("/service/<int:service_id>")
@login_required
def service(service_id):
  with app.app_context():
    service = Service.query.get_or_404(service_id)
  with app.app_context():
        offered_by_professionals = Service_Professional.query.filter_by(service_id=service_id).all()
        offered_by_professionals = [{"name":professional.username, "email":professional.email, "description":professional.description, "experience": professional.experience, "date_created":professional.date_created} for professional in offered_by_professionals]
  return render_template('service.html', name=service.name, service=service, offered_by_professionals=offered_by_professionals)

 
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
    flash(f"Access Denied! Only Customer can request Service", "danger")
    return redirect(url_for("home"))
   else:
      form = ServiceRequestForm()
      if form.validate_on_submit():
        if len(Service_Request.query.filter(Service_Request.customer_id==current_user.id,  func.lower(Service_Request.service_status) != "COMPLETED".lower()).all()) == 5:
         flash('You have already requested 5 services. Mark a service as complete to request this!', 'danger')
         return redirect(url_for('home'))
        elif len(Service_Request.query.filter(Service_Request.customer_id==current_user.id, Service_Request.service_id==service_id).all()) > 0:
           flash('You have already requested this service!', 'danger')
           return redirect(url_for('home'))
        elif len(Service_Request.query.filter(Service_Request.customer_id==current_user.id,Service_Request.service_id==service_id).all()) > 0 and Service_Request.query.filter_by(customer_id=current_user.id,service_id=service_id).first().service_status == "YET_TO_ASSIGN":
           flash('You have already requested this service! Wait for admin approval of previous request.', 'danger')
           return redirect(url_for('home'))
        else:
         customer_id = current_user.id
         duration = form.request_duration.data
         td = duration_to_timedelta(duration)
         date_of_completion = form.date_of_request.data + td
         with app.app_context():
            free_service_professionals = []
            for service_professional in Service_Professional.query.filter_by(service_id=service_id):
               if service_professional.service_requests:
                  for service_request in service_professional.service_requests:
                     if service_request.service_status != "assigned" and service_request.date_of_completion < datetime.now():
                        free_service_professionals.append(service_professional)
               else:
                  free_service_professionals.append(service_professional)
            
            if free_service_professionals:
               to_be_assigned = free_service_professionals.pop(0)
               status = "assigned"
               br = Service_Request(date_of_request=form.date_of_request.data, service_professional_id=to_be_assigned.id,customer_id=customer_id, service_id=service_id, date_of_completion=date_of_completion, service_status=status)
            else:
               status = "requested"
               br = Service_Request(date_of_request=form.date_of_request.data ,customer_id=customer_id, service_id=service_id, date_of_completion=date_of_completion, service_status=status)

            db.session.add(br)
            db.session.commit()
            flash('Service Requested Successfully!', 'success')
            return redirect(url_for('home'))
      return render_template('add_service_request.html', title="Request this service", form=form)
 


@app.route("/complete-request/<int:request_id>", methods=['GET', 'POST'])
@login_required
def mark_request_as_complete(request_id):
   if current_user.role != "customer":
      flash(f"Access Denied! You do not have permission to view this page.", "danger")
      return redirect(url_for("home"))
   with app.app_context():
      request = Service_Request.query.filter_by(id=request_id).first()
      request.service_status = "completed" # type: ignore
      db.session.commit()
   flash(f"Marked the service request as complete!", "danger")
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
      with app.app_context():
         db.session.add(remark)
         db.session.commit()
      flash(f"Remarks submitted successfully!", "success")
      return redirect(url_for('home'))
   return render_template('submit_remark.html', title='Submit Remarks', form=form)

@app.route("/cancel/<int:request_id>", methods=['GET', 'POST'])
@login_required
def cancel_request(request_id):
   if current_user.role != "customer":
      flash(f"Access Denied! You do not have permission to view this page.", "danger")
      return redirect(url_for("home"))
   with app.app_context():
      request = Service_Request.query.filter_by(id=request_id).first()
      db.session.delete(request)
      db.session.commit()
   flash(f"Cancelled the service request!", "danger")
   return redirect(url_for('home'))


@app.route('/customer-requests')
@login_required
def customer_requests():
   if current_user.role != 'customer':
      flash(f"Access Denied! Only Customers view requested books", "danger")
      return redirect(url_for("home"))
   else:
      service_requests = Service_Request.query.filter_by(customer_id=current_user.id).all() # type: ignore
      details = []
      service_name = ""
      customer_name = ""
      service_professional_name = ""
      service_id = ""
      customer_id = ""
      service_professional_id = ""
      service_status = ""
      date_of_request = ""
      date_of_completion = ""
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

         details.append({'request_id':service_request.id,'service_name':service_name, 'customer_name': customer_name,'service_professional_name': service_professional_name,'service_id': service_id, 'customer_id': customer_id,'service_professional_id': service_professional_id,'service_status': service_status, 'date_of_request': date_of_request, 'date_of_completion': date_of_completion}) # type: ignore
      return render_template('customer_requests.html', requested_services=details, title='Requests')






@app.route("/customer-graphs")
@login_required
def customer_graphs():
  #  if current_user.role == 'librarian':
  #     flash("Access Denied! You do not have permission to view this page.", "danger")
  #     return redirect(url_for("home"))
  #  issued_books = BookIssue.query.filter_by(student_id=current_user.id).all()
  #  values = [k.name for i in issued_books for j in Book.query.filter_by(id=i.book_id).all() for k in Genre.query.filter_by(id=j.genre_id).all()]
  #  value_counts = {}
  #  for value in values:
  #     value_counts[value] = value_counts.get(value, 0) + 1

  #  # Pie chart
  #  plt.figure(figsize=(8, 8))
  #  plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140)
  #  plt.axis('equal')
  #  plt.title('Distribution of Genres in Issued Books')
  #  picture_path = os.path.join(app.root_path, f'static/graphs/one.png')
  #  plt.savefig(picture_path)
  #  plt.close()

  #  image = save_graph(picture_path, 'student')
  #  image_url = url_for('static', filename='graphs/' + image)

  #  genres = [i.name for i in Genre.query.all()]
  #  value_counts = {}
  #  for value in genres:
  #     value_counts[value] = value_counts.get(value, 0) + 1

  #  # Pie chart
  #  plt.figure(figsize=(8, 8))
  #  plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140)
  #  plt.axis('equal')
  #  plt.title('Distribution of Genres Available')
  #  picture_path = os.path.join(app.root_path, f'static/graphs/two.png')
  #  plt.savefig(picture_path)
  #  plt.close()

  #  image1 = save_graph(picture_path, 'all')
  #  image_url1 = url_for('static', filename='graphs/' + image1)

   return render_template('home.html', image="", image1="", title="Graph")

 

@app.route("/sp-graphs")
@login_required
def sp_graphs():
   return render_template('home.html', image="", image1="", title="Graph")
#    if current_user.role != 'librarian':
#       flash("Access Denied! You do not have permission to view this page.", "danger")
#       return redirect(url_for("home"))
#    issued_books = BookIssue.query.all()
#    values = [k.name for i in issued_books for j in Book.query.filter_by(id=i.book_id).all() for k in Genre.query.filter_by(id=j.genre_id).all()]
#    value_counts = {}
#    for value in values:
#       value_counts[value] = value_counts.get(value, 0) + 1

#    # Pie chart
#    plt.figure(figsize=(8, 8))
#    plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140)
#    plt.axis('equal')
#    plt.title('Distribution of Genres in Issued Books')
#    picture_path = os.path.join(app.root_path, f'static/graphs/three.png')
#    plt.savefig(picture_path)
#    plt.close()

#    image = save_graph(picture_path, 'librarian')
#    image_url = url_for('static', filename='graphs/' + image)

#    genres = [i.name for i in Genre.query.all()]
#    value_counts = {}
#    for value in genres:
#       value_counts[value] = value_counts.get(value, 0) + 1

#    # Pie chart
#    plt.figure(figsize=(8, 8))
#    plt.pie(value_counts.values(), labels=value_counts.keys(), autopct='%1.1f%%', startangle=140)
#    plt.axis('equal')
#    plt.title('Distribution of Genres Available')
#    picture_path = os.path.join(app.root_path, f'static/graphs/four.png')
#    plt.savefig(picture_path)
#    plt.close()

#    image1 = save_graph(picture_path, 'all')
#    image_url1 = url_for('static', filename='graphs/' + image1)

#    return render_template('graph.html', image=image_url, image1=image_url1, title="Graph")


@app.route('/pending-requests')
@login_required
def pending_requests():
   if current_user.role != "customer":
     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
     return redirect(url_for("home"))
   
   requests = Service_Request.query.filter_by(customer_id=current_user.id, service_status="requested").all()
   return render_template('pending_requests.html', title="Pending Requests", requests=requests)
   




# @app.route("/section/<int:section_id>/update", methods=['GET', 'POST'])
# @login_required
# def update_section(section_id):
#   if current_user.role != "librarian":
#     flash(f"Access Denied! You do not have permission to view this page.{current_user.role} acc", "danger")
#     return redirect(url_for("home"))
  
#   section = Genre.query.get_or_404(section_id)
#   form = SectionForm()
#   if form.validate_on_submit():
#      if section.name.lower() != form.title.data.lower() and len(Genre.query.filter(func.lower(Genre.name).ilike(f"%{form.title.data.lower()}%")).all()) > 0:
#            flash('Section with that name already exists!', 'danger')
#            return redirect(url_for('update_section', section_id=section_id))
#      section.name = form.title.data
#      section.description = form.content.data
#      section.date_created = form.date_created.data
#      section.librarian_id = current_user.id
#      db.session.commit()
#      flash(f'Updated the Section successfully', 'success')
#      return redirect(url_for('section', section_id=section.id))
#   elif request.method == 'GET':
#     form.title.data = section.name
#     form.content.data = section.description
#     form.date_created.data = section.date_created
#   return render_template('create_section.html', title='Update Section', section=section, form=form, legend='Update Section')



# @app.route("/section/<int:section_id>/<int:book_id>/delete", methods=['POST'])
# @login_required
# def delete_book(section_id, book_id):
#   if current_user.role != "librarian":
#     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
#     return redirect(url_for("home"))
  
#   with app.app_context():
#      book = Book.query.get_or_404(book_id)
     
#      feedbacks = FeedBack.query.filter_by(book_id=book_id).all()
#      for feedback in feedbacks:
#            db.session.delete(feedback)
#            db.session.commit()
     
#      db.session.delete(book)
#      db.session.commit()
#      flash('Book Deleted!', 'success')
#      return redirect(url_for('section', section_id=section_id))

  
# @app.route('/student-requests')
# @login_required
# def student_requests():
#    if current_user.role == 'librarian':
#       flash(f"Access Denied! Only Students view requested books", "danger")
#       return redirect(url_for("home"))
#    else:
#       requested_books = BookRequest.query.filter_by(student_id=current_user.id).all()
#       details = [[Book.query.filter_by(id=x.book_id).first().title, BookRequest.query.filter_by(id=x.id).first().request_duration] for x in requested_books]
#    return render_template('student_requests.html', requested_books=details, title='Requests')


  



# @app.route("/pending-requests/<int:request_id>/issue", methods=['POST'])
# @login_required
# def issue_book(request_id):
#   if current_user.role != "librarian":
#     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
#     return redirect(url_for("home"))
  
#   with app.app_context():
#      book_request = BookRequest.query.get_or_404(request_id)
#      issue_date = datetime.now()
#      return_date = issue_date + duration_to_timedelta(book_request.request_duration)
#      student_id = book_request.student_id
#      book_id = book_request.book_id
#      librarian_id = current_user.id

#      bi = BookIssue(issue_date=issue_date,return_date=return_date,student_id=student_id,book_id=book_id,librarian_id=librarian_id)
#      db.session.add(bi)
#      db.session.commit()

#      db.session.delete(book_request)
#      db.session.commit()
#      flash('Book Issued to Student!', 'success')
#   return redirect(url_for('pending_requests'))

# @app.route("/pending-requests/<int:request_id>/disapprove", methods=['POST'])
# @login_required
# def disapprove_request(request_id):
#   if current_user.role != "librarian":
#     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
#     return redirect(url_for("home"))
  
#   with app.app_context():
#      book_request = BookRequest.query.get_or_404(request_id)
#      db.session.delete(book_request)
#      db.session.commit()
#      flash('Book Request disapproved to Student!', 'danger')
#   return redirect(url_for('pending_requests'))

# @app.route("/student-issued")
# @login_required
# def student_issued():
#   if current_user.role == "librarian":
#     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
#     return redirect(url_for("home"))
#   else:
#      books = BookIssue.query.filter_by(student_id=current_user.id).all()
#      books = [Book.query.filter_by(id=book.book_id).all()+[book.return_date, Genre.query.filter_by(id=Book.query.filter_by(id=book.book_id).first().genre_id).first().name, book.id] for book in books]
#   return render_template('student_issued_books.html', issued_books=books, title='Issued books')


# @app.route("/revoke-access/<int:issue_id>", methods=['POST'])
# @login_required
# def revoke_access(issue_id):
#    if current_user.role != "librarian":
#     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
#     return redirect(url_for("home"))
#    else:
#       with app.app_context():
#          book_issue = BookIssue.query.filter_by(id=issue_id).first()
#          db.session.delete(book_issue)
#          db.session.commit()
#       flash(f"Access revoked", "danger")   
#       return redirect(url_for('sp_dash'))
   
# @app.route("/return-book/<int:issue_id>", methods=['POST'])
# @login_required
# def return_book(issue_id):
#    if current_user.role == "librarian":
#     flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
#     return redirect(url_for("home"))
#    else:
#       with app.app_context():
#          book_issue = BookIssue.query.filter_by(id=issue_id).first()
#          bid = book_issue.book_id
#          sid = book_issue.student_id
#          db.session.delete(book_issue)
#          db.session.commit()
#       return redirect(url_for('book_feedback', book_id=bid, student_id=sid))
   

# @app.route('/book-feedback/<int:book_id>/<int:student_id>', methods=['GET', 'POST'])
# @login_required
# def book_feedback(book_id, student_id):
#    if current_user.role == "librarian" or current_user.id != student_id:
#     flash("Access Denied! You do not have permission to view this page.", "danger")
#     return redirect(url_for("home"))
#    else:
#       bname = Book.query.filter_by(id=book_id).first().title
#       sname = Student.query.filter_by(id=student_id).first().username

#       form = FeedBackForm()
#       if form.validate_on_submit():
#         feedback = form.feedback.data
#         if len(feedback) >= 200:
#            flash("Limit your feedback to less than or equal to 200 words.", "danger")
#            return redirect(url_for('book_feedback', book_id=book_id, student_id=student_id))
#         with app.app_context():
#             f = FeedBack(feedback=feedback,student_id=student_id, book_id=book_id)
#             db.session.add(f)
#             db.session.commit()
#             flash('Feedback Submitted Successfully!', 'success')
#             return redirect(url_for('home'))

#       return render_template('feedback.html', book_name=bname, student_name=sname, legend='Feedback Form', form=form, title="Book Feedback")
   


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
   

# def save_graph(filename, role):
#    _, ext = os.path.splitext(filename)
#    picture_fn = f"{role}_available" + ext
#    picture_path = os.path.join(app.root_path, f'static/graphs', picture_fn)
   
#    i = Image.open(filename)
#    i.save(picture_path)
   
#    return picture_fn


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
   