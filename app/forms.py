from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if not email.data.endswith('@southernct.edu'):
            raise ValidationError('Please use your SCSU email (@southernct.edu)')
        
class CreateStudyGroupForm(FlaskForm):
    title = StringField('Group Title', validators=[DataRequired(), Length(max=100)])
    subject = StringField('Subject/Course', validators=[DataRequired(), Length(max=100)])
    tags = StringField('Tags (comma separated)', validators=[Length(max=200)])
    session = StringField('Preferred Meeting Time', validators=[Length(max=100)])
    submit = SubmitField('Create Group')