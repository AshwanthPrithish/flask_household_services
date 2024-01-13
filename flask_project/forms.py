from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from flask_project.models import Student, Librarian

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