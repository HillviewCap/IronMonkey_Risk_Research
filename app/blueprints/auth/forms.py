from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models.user import User
from app import db
from sqlalchemy import text

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        result = db.session.execute(
            text("SELECT id FROM users.users_accounts WHERE username = :username"),
            {'username': username.data}
        )
        user = result.fetchone()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        result = db.session.execute(
            text("SELECT id FROM users.users_accounts WHERE email = :email"),
            {'email': email.data}
        )
        user = result.fetchone()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')