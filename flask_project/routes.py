import secrets
import os

from datetime import datetime
from PIL import Image
from flask import render_template,flash, redirect, url_for, request
from flask_project import app, db, bcrypt
from flask_project.forms import RegistrationForm, LoginForm, SPRegistrationForm, SPLoginForm, UpdateStudentAccount, UpdateSPAccount, SectionForm, BookAddForm
from flask_project.models import Student, Librarian, Book, BookIssue, Genre
from flask_login import login_user, current_user, logout_user, login_required

with app.app_context():
  db.create_all()

@app.route("/")
@app.route("/home")
def home():
  return render_template("home.html", title="Home")

@app.route("/student-dash")
@login_required
def student_dash():
  if current_user.role == "student":
       return render_template("student_dashboard.html", title="Student Dashboard")
  else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))

@app.route("/sp-dash")
@login_required
def sp_dash():
  if current_user.role == "librarian":
       return render_template("sp_dashboard.html", title="Librarian Dashboard")
  else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))


@app.route("/sections")
def sections():
  with app.app_context():
     sections_ = Genre.query.all()
  return render_template("sections.html", section_list=sections_, title="Book List")

@app.route("/about-us")
def about_us():
  return render_template("about_us.html", title="About us")

@app.route("/contact")
def contact():
  return render_template("contact.html", title="Contact")


@app.route("/register", methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    if current_user.role == "student":
       return redirect(url_for('student_dash'))
    else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
  form = RegistrationForm()
  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    student = Student(username=form.username.data, email=form.email.data, password=hashed_password)
    with app.app_context():
      db.session.add(student)
      db.session.commit()

    flash(f'Your Student Account has been created!', 'success')
    return redirect(url_for("login"))
  return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if current_user.is_authenticated:
    if current_user.role == "student":
       return redirect(url_for('student_dash'))
    else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
  if form.validate_on_submit():
    student = Student.query.filter_by(email=form.email.data).first()
    if student and bcrypt.check_password_hash(student.password, form.password.data):
      login_user(student, remember=form.remember.data)
      return redirect(url_for('student_dash'))
    else:
      flash('Login unsuccessful, please check email, and password', 'danger')
  return render_template("login.html", title="Login", form=form)

@app.route("/sp-register", methods=['GET', 'POST'])
def sp_register():
  if current_user.is_authenticated:
    if current_user.role == "librarian":
       return redirect(url_for('sp_dash'))
    else:
       flash("Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
  form = SPRegistrationForm()
  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    librarian = Librarian(username=form.username.data, email=form.email.data, admin_id=form.admin_id.data, password=hashed_password)
    with app.app_context():
      db.session.add(librarian)
      db.session.commit()

    flash(f'Account Created for Admin {form.username.data}!', 'success')
    return redirect(url_for("sp_login"))
  return render_template("sp_register.html", title="Admin Register", form=form)

@app.route("/sp-login", methods=['GET', 'POST'])
def sp_login():
  form = SPLoginForm()
  if current_user.is_authenticated:
    if current_user.role == "librarian":
       return redirect(url_for('sp_dash'))
    else:
       flash(f"Access Denied! You do not have permission to view this page.", "danger")
       return redirect(url_for("home"))
  
  if form.validate_on_submit():
    librarian = Librarian.query.filter_by(email=form.email.data).first()
    if librarian and bcrypt.check_password_hash(librarian.password, form.password.data):
      login_user(librarian, remember=form.remember.data)
      return redirect(url_for('sp_dash'))
    else:
      flash('Login unsuccessful, please check email, and password', 'danger')
  return render_template("sp_login.html", title="Admin Login", form=form)

@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for('home'))


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
  if current_user.role == "student":
        form = UpdateStudentAccount()
        if form.validate_on_submit():
            if form.picture.data:
               picture_file = save_picture(form.picture.data, 'student_pics')
               with app.app_context():
                current_user.image_file = picture_file
                db.session.commit()
            with app.app_context():
              current_user.username = form.username.data
              current_user.email = form.email.data
              db.session.commit()
            flash('Your Account has been updated!', category='success')
            return redirect(url_for('account'))
        elif request.method == "GET":
           form.username.data = current_user.username
           form.email.data = current_user.email
        image_file = url_for('static', filename='profile_pics/student_pics/' + current_user.image_file)
        return render_template("student_account.html", title="Student Account", image_file=image_file, form=form)
  
  elif current_user.role == "librarian":
        form = UpdateSPAccount()
        if form.validate_on_submit():
            if form.picture.data:
               picture_file = save_picture(form.picture.data, 'admin_pics')
               with app.app_context():
                current_user.image_file = picture_file
                db.session.commit()
            with app.app_context():
              current_user.username = form.username.data
              current_user.email = form.email.data
              current_user.admin_id = form.admin_id.data
              db.session.commit()
            flash('Your Account has been updated!', category='success')
            return redirect(url_for('account'))
        elif request.method == "GET":
           form.username.data = current_user.username
           form.email.data = current_user.email
           form.admin_id.data = current_user.admin_id
        image_file = url_for('static', filename='profile_pics/admin_pics/' + current_user.image_file)
        return render_template("sp_account.html", title="Librarian Account", image_file=image_file, form=form)
  
  else:
        flash(f"Access Denied! You do not have permission to view this page.{current_user.role} acc", "danger")
        return redirect(url_for("home"))
  
@app.route("/section/new", methods=['GET', 'POST'])
@login_required
def new_section():
  if current_user.role != "librarian":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role} acc", "danger")
    return redirect(url_for("home"))
  
  form = SectionForm()
  if form.validate_on_submit():
      if form.date_created.data == '':
        section = Genre(name=form.title.data, description=form.content.data, librarian_username=current_user.username)
      else:
        d = form.date_created.data
        section = Genre(name=form.title.data, description=form.content.data, date_created=d, librarian_username=current_user.username)
      with app.app_context():
         db.session.add(section)
         db.session.commit()
         flash('The Section has been created!', 'success')
      return redirect(url_for('sections'))
  return render_template('create_section.html', title="New Section", form=form, legend='New Section')
  
@app.route("/section/<int:section_id>")
def section(section_id):
  with app.app_context():
    section = Genre.query.get_or_404(section_id)
  with app.app_context():
        books = Book.query.filter_by(genre_id=section_id).all()
  return render_template('section.html', title=section.name, section=section, book_list=books)

@app.route("/section/<int:section_id>/update", methods=['GET', 'POST'])
@login_required
def update_section(section_id):
  if current_user.role != "librarian":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role} acc", "danger")
    return redirect(url_for("home"))
  
  section = Genre.query.get_or_404(section_id)
  form = SectionForm()
  if form.validate_on_submit():
     section.name = form.title.data
     section.description = form.content.data
     section.date_created = form.date_created.data
     section.librarian_username = current_user.username
     db.session.commit()
     flash(f'Updated the Section successfully', 'success')
     return redirect(url_for('section', section_id=section.id))
  elif request.method == 'GET':
    form.title.data = section.name
    form.content.data = section.description
    form.date_created.data = section.date_created
  return render_template('create_section.html', title='Update Section', section=section, form=form, legend='Update Section')

@app.route("/section/<int:section_id>/delete", methods=['POST'])
@login_required
def delete_section(section_id):
  if current_user.role != "librarian":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
    return redirect(url_for("home"))
  
  with app.app_context():
     section = Genre.query.get_or_404(section_id)
     db.session.delete(section)
     db.session.commit()
     flash('Section Deleted!', 'success')
     return redirect(url_for('sections'))
  
@app.route("/section/<int:section_id>/add-book", methods=['GET', 'POST'])
@login_required
def add_book(section_id):
  if current_user.role != "librarian":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role} acc", "danger")
    return redirect(url_for("home"))
  
  form = BookAddForm()
  if form.validate_on_submit():
     book = Book(title=form.title.data,author=form.author.data,content=form.content.data,rating=form.rating.data,release_year=form.release_year.data,librarian_id=current_user.id,genre_id=section_id)
     with app.app_context():
        db.session.add(book)
        db.session.commit()
        flash('The Book has been Added Successfully.', 'success')
     
     return redirect(url_for('section', section_id=section_id))
  
  return render_template('add_book.html', title="Add a new Book", form=form, legend='New Book')

@app.route("/section/<int:section_id>/<int:book_id>/update-book", methods=['GET', 'POST'])
@login_required
def update_book(section_id, book_id):
  if current_user.role != "librarian":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role} acc", "danger")
    return redirect(url_for("home"))
  
  book = Book.query.get_or_404(book_id)
  form = BookAddForm()
  if form.validate_on_submit():
     
        book.title=form.title.data
        book.author=form.author.data
        book.content=form.content.data
        book.rating=form.rating.data
        book.release_year=form.release_year.data
        db.session.commit()
        flash(f'The Book has been Updated Successfully.', 'success')
    
        return redirect(url_for('section', section_id=section_id))
  elif request.method == 'GET':
    form.title.data = book.title
    form.author.data = book.author
    form.content.data = book.content
    form.rating.data = book.rating
    form.release_year.data = book.release_year

     
  return render_template('add_book.html', title="Update this Book", form=form, legend='Update Book')

@app.route("/section/<int:section_id>/<int:book_id>/delete", methods=['POST'])
@login_required
def delete_book(section_id, book_id):
  if current_user.role != "librarian":
    flash(f"Access Denied! You do not have permission to view this page.{current_user.role}", "danger")
    return redirect(url_for("home"))
  
  with app.app_context():
     book = Book.query.get_or_404(book_id)
     db.session.delete(book)
     db.session.commit()
     flash('Book Deleted!', 'success')
     return redirect(url_for('section', section_id=section_id))