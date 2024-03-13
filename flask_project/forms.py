from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField, TextAreaField, IntegerField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from flask_project.models import Student, Librarian, Genre, Book
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Regexp("^\d{5,8}$")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('That username is taken. Please choose a new one.')
        
    def validate_email(self, email):
        student = Student.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('Student with that email already exits. Try a new one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class SPRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    admin_id = StringField('Admin ID', validators=[DataRequired(), Length(min=2, max=20), Regexp("^\d{5,8}$")])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        librarian = Librarian.query.filter_by(username=username.data).first()
        if librarian:
            raise ValidationError('That username is taken. Please choose a new one.')
        
    def validate_email(self, email):
        librarian = Librarian.query.filter_by(email=email.data).first()
        if librarian:
            raise ValidationError('Librarian with that email already exits. Try a new one.')
        
    def validate_admin_id(self, admin_id):
        librarian = Librarian.query.filter_by(admin_id=admin_id.data).first()
        if librarian:
            raise ValidationError('Librarian with that Admin ID already exits. Try a another one.')
        elif int(admin_id.data) not in [48236, 76541, 23985, 50472, 19847, 65329, 31784, 92651, 84063, 57214]:
            raise ValidationError(f'Unauthorized Admin ID. Contact Organization for further action.')

class SPLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class UpdateStudentAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            student = Student.query.filter_by(username=username.data).first()
            if student:
                raise ValidationError('That username is taken. Please choose a new one.')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            student = Student.query.filter_by(email=email.data).first()
            if student:
                raise ValidationError('Student with that email already exits. Try a new one.')
            
class UpdateSPAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    admin_id = StringField('Admin ID', validators=[DataRequired(), Length(min=2, max=20), Regexp("^\d{5,8}$")])
    picture = FileField('Update Profile picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            librarian = Librarian.query.filter_by(username=username.data).first()
            if librarian:
                raise ValidationError('That username is taken. Please choose another one.')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            librarian = Librarian.query.filter_by(email=email.data).first()
            if librarian:
                raise ValidationError('Librarian with that email already exits. Try another one.')
    
    def validate_admin_id(self, admin_id):
        if admin_id.data != current_user.admin_id:
            librarian = Librarian.query.filter_by(admin_id=admin_id.data).first()
            if librarian:
                raise ValidationError('Librarian with that admin ID already exits. Try another one.')
            elif int(admin_id.data) not in [48236, 76541, 23985, 50472, 19847, 65329, 31784, 92651, 84063, 57214]:
                raise ValidationError(f'Unauthorized Admin ID. Contact Organization for further action.')
            
class SectionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    date_created = DateTimeField('Date Added(Format dd-mm-yyyy)', format="%d-%m-%Y", validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField()
    
class BookAddForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    lang = StringField('Language', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    rating = IntegerField('Rating', validators=[DataRequired()])
    release_year = DateTimeField('Release Year(yyyy)', format="%Y", validators=[DataRequired()])
    submit = SubmitField()


class BookRequestForm(FlaskForm):
    request_duration = StringField('Period of Borrowing/days/weeks):(Eg: Enter "7 hours,6 days, 8 weeks" to borrow for 7 hours, 6 days, and 8 weeks', validators=[DataRequired()])
    submit = SubmitField()

class FeedBackForm(FlaskForm):
    feedback = StringField('Feedback for Book', validators=[DataRequired()])
    skipper = BooleanField('Skip Feedback?')
    submit = SubmitField()

class SearchSectionForm(FlaskForm):
    section = StringField('Enter the Section to search for:', validators=[DataRequired()])
    submit = SubmitField()

class SearchTitleForm(FlaskForm):
    title = StringField('Enter the Book Title to search for:', validators=[DataRequired()])
    submit = SubmitField()

class SearchAuthorForm(FlaskForm):
    author = StringField('Enter the Author name to search for:', validators=[DataRequired()])
    submit = SubmitField()