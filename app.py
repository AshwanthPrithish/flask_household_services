from flask import Flask, render_template,flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, SPRegistrationForm, SPLoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cf5502128e89ac7e636ca2dd6c913212'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class GeneralUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.username}'), '{self.email}', '{self.image_file}'"

class SPUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  admin_id = db.Column(db.Integer, unique=True, nullable=False)
  image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.username}'), '{self.email}', '{self.image_file}'"

class Book(db.Model):
  id = db.Column(db.String(20), unique=True, nullable=False)
  title = db.Column(db.String(100), unique=True, nullable=False)
  author = db.Column(db.String(100), unique=True, nullable=False)
  genre = db.Column(db.String(100), unique=True, nullable=False)
  rating = db.Column(db.Integer, unique=True, nullable=False)

BOOKS = [
    {
        "book_id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Classic",
        "rating": 7.5,
        "release_year": 1925
    },
    {
        "book_id": 2,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Fiction",
        "release_year": 1960
    },
    {
        "book_id": 3,
        "title": "1984",
        "author": "George Orwell",
        "genre": "Dystopian",
        "rating": 8,
        "release_year": 1949
    },
    {
        "book_id": 4,
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasy",
        "release_year": 1937
    },
    {
        "book_id": 5,
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "genre": "Coming-of-age",
        "release_year": 1951
    }
]

@app.route("/")
@app.route("/home")
def home():
  return render_template("home.html", title="Home")

@app.route("/books")
def books():
  return render_template("books.html", book_list=BOOKS, title="Book List")

@app.route("/about-us")
def about_us():
  return render_template("about_us.html", title="About us")

@app.route("/contact")
def contact():
  return render_template("contact.html", title="Contact")

@app.route("/general-user")
def general_user():
  return render_template("general_user.html", title="General User")

@app.route("/librarian")
def librarian():
  return render_template("librarian.html", title="Librarian")


@app.route("/register", methods=['GET', 'POST'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    flash(f'Account Created for {form.username.data}!', 'success')
    return redirect(url_for("home"))
  return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    if form.email.data == 'admin@blog.com' and form.password.data == 'password':
      flash('You have been logged in!', 'success')
      return redirect(url_for('home'))
    else:
      flash('Login unsuccessful, please check username, and password', 'danger')
  return render_template("login.html", title="Login", form=form)

@app.route("/sp-register", methods=['GET', 'POST'])
def sp_register():
  form = SPRegistrationForm()
  if form.validate_on_submit():
    flash(f'Account Created for {form.username.data}!', 'success')
    return redirect(url_for("home"))
  return render_template("sp_register.html", title="Admin Register", form=form)

@app.route("/sp-login", methods=['GET', 'POST'])
def sp_login():
  form = SPLoginForm()
  if form.validate_on_submit():
    if form.email.data == 'admin@blog.com' and form.password.data == 'password':
      flash('You have been logged in!', 'success')
      return redirect(url_for('home'))
    else:
      flash('Login unsuccessful, please check username, and password', 'danger')
  return render_template("sp_login.html", title="Admin Login", form=form)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
