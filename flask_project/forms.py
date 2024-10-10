from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField, StringField, PasswordField, SubmitField, BooleanField, DateTimeField, TextAreaField, IntegerField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from flask_project.models import Customer, Service_Professional, Service, Remarks
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=50)])
    contact = StringField('Contact', validators=[DataRequired(), Length(min=9, max=10)])
    password = PasswordField("Password", validators=[DataRequired(), Regexp(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&+=]{5,8}$")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        customer = Customer.query.filter_by(username=username.data).first()
        if customer:
            raise ValidationError('That username is taken. Please choose a new one.')
        
    def validate_email(self, email):
        customer = Customer.query.filter_by(email=email.data).first()
        if customer:
            raise ValidationError('Customer with that email already exits. Try a new one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class SPRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Regexp(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&+=]{5,8}$")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=2, max=100)])
    experience = StringField('Experience', validators=[DataRequired(), Length(min=2, max=20)])
    service = SelectField('Service', choices=[]) 
    
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        librarian = Service_Professional.query.filter_by(username=username.data).first()
        if librarian:
            raise ValidationError('That username is taken. Please choose a new one.')
        
    def validate_email(self, email):
        librarian = Service_Professional.query.filter_by(email=email.data).first()
        if librarian:
            raise ValidationError('Librarian with that email already exits. Try a new one.')

class UpdateCustomerAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=50)])
    contact = StringField('Contact', validators=[DataRequired(), Length(min=9, max=10)])
    picture = FileField('Update Profile picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            customer = Customer.query.filter_by(username=username.data).first()
            if customer:
                raise ValidationError('That username is taken. Please choose a new one.')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            customer = Customer.query.filter_by(email=email.data).first()
            if customer:
                raise ValidationError('That email already exits. Try a new one.')


class SPLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

            
class UpdateSPAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=2, max=100)])
    experience = StringField('Experience', validators=[DataRequired(), Length(min=2, max=20)])
    service = SelectField('Service', choices=[]) 
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            service_professional = Service_Professional.query.filter_by(username=username.data).first()
            if service_professional:
                raise ValidationError('That username is taken. Please choose another one.')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            service_professional = Service_Professional.query.filter_by(email=email.data).first()
            if service_professional:
                raise ValidationError('That email already exits. Try another one.')


class ServiceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField()
    
# class BookAddForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     author = StringField('Author', validators=[DataRequired()])
#     lang = StringField('Language', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     rating = IntegerField('Rating', validators=[DataRequired()])
#     release_year = DateTimeField('Release Year(yyyy)', format="%Y", validators=[DataRequired()])
#     submit = SubmitField()


# class BookRequestForm(FlaskForm):
#     request_duration = StringField('Period of Borrowing/days/weeks):(Eg: Enter "7 hours,6 days, 8 weeks" to borrow for 7 hours, 6 days, and 8 weeks', validators=[DataRequired()])
#     submit = SubmitField()

# class FeedBackForm(FlaskForm):
#     feedback = StringField('Feedback for Book', validators=[DataRequired()])
#     skipper = BooleanField('Skip Feedback?')
#     submit = SubmitField()

class SearchServiceForm(FlaskForm):
    service = StringField('Enter the service to search for:', validators=[DataRequired()])
    submit = SubmitField()

class SearchServiceProfessionalForm(FlaskForm):
    service_professional = StringField('Enter the service professional to search for:', validators=[DataRequired()])
    submit = SubmitField()