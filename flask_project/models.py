from flask_project import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    # Assuming that the user_id is the primary key of your User model
    user = None
    
    if (int(user_id) >= 10000):
        user = Librarian.query.filter_by(id=int(user_id)).first()
    else:
        # Try to load the user as a Student
        user = Student.query.filter_by(id=int(user_id)).first()
    
    return user

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    book_issues = db.relationship('BookIssue', backref='student', lazy=True)
    role = "student"

    def __repr__(self):
        return f"Student('{self.username}', '{self.email}', '{self.image_file}')"

class Librarian(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    admin_id = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    books = db.relationship('Book', backref='librarian_admin', lazy=True)
    genres = db.relationship('Genre', backref='librarian_admin', lazy=True)
    book_issues = db.relationship('BookIssue', backref='librarian', lazy=True)
    role = "librarian"

    def __repr__(self):
        return f"Librarian('{self.username}', '{self.email}', '{self.image_file}')"
    
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(100), nullable=False, default="Description yet to be added.")
    books = db.relationship('Book', backref='genre_of_book', lazy=True)
    librarian_username = db.Column(db.String(20), db.ForeignKey('librarian.username'), nullable=False)

    def __repr__(self):
        return f"Genre('{self.name}', {self.books})"

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    release_year = db.Column(db.DateTime, nullable=False, default=datetime.now)
    librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'), nullable=False)
    book_issues = db.relationship('BookIssue', backref='book', lazy=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}')"

class BookIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'), nullable=False)

    def __repr__(self):
        return f"BookIssue('{self.issue_date}', '{self.return_date}')"

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_duration = db.Column(db.String(100), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    def __repr__(self):
        return f"BookRequest('{self.id}', '{self.request_duration}')"

class FeedBack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    feedback = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"FeedBack('{self.id}')"