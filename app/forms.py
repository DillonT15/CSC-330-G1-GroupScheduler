from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from app.models import *


#Login/registration no longer requires username
class LoginForm(FlaskForm):
    email = StringField('SCSU Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('SCSU Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if not email.data.endswith('@southernct.edu'):
            raise ValidationError('Please use your SCSU email (@southernct.edu)')
        #Additional check to see if the email is already in the database. prevents duplicates
        existing_user = User.query.filter_by(email=email.data).first()
        if existing_user:
            raise ValidationError('An account with this email already exists.')
        

class CreateStudyGroupForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    # Dropdown for subject selection needs to be added to database - Also we may want a global enum list for this to not repeat
    subject = SelectField(
    'Subject',
    choices=[
        ('CS',   'Computer Science'),
        ('MATH', 'Mathematics'),
        ('PHYS', 'Physics'),
        ('BIO',  'Biology'),
        ('ENG',  'English'),
        ('HIS', 'History'),
        ('OTHER', 'Other')
    ],
    validators=[DataRequired()]
    )
    course = StringField('Course', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    time = StringField('Meeting Time', validators=[DataRequired(), Length(max=100)]) # Should use a time picker or something
    tags = StringField('Tags (comma-separated)', validators=[Length(max=200)])
    submit = SubmitField('Create Study Group')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=100)])
    major = StringField('Major', validators=[Length(max=100)])
    new_password = PasswordField('New Password', validators=[Length(min=6)], render_kw={"placeholder": "Leave blank to keep current password"})
    confirm = PasswordField('Confirm New Password', validators=[EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Update Profile')