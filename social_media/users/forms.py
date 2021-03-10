
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from social_media.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


    def validate_username(self, username):
        user = User.query.filter_by(username= username.data).first()
        if user:
            raise ValidationError('That username is taken. Choose a different one')
    
    def validate_email(self, email):
        user = User.query.filter_by(email= email.data).first()
        if user:
            raise ValidationError('That email is taken. Choose a different one')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    def validate_email(self, email):
        user = User.query.filter_by(email= email.data).first()
        if user is None:
            raise ValidationError('You are not a registered user. You must register first')



class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    pics = FileField('Upadte Profile Picture', validators=[FileAllowed(['jpg','png','svg'])])                    
    
    submit = SubmitField('Update')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username= username.data).first()
            if user:
                raise ValidationError('That username is taken. Choose a different one')
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email= email.data).first()
            if user:
                raise ValidationError('That email is taken. Choose a different one')


class ResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    
    submit = SubmitField('Reset')
    def validate_email(self, email):
        user = User.query.filter_by(email= email.data).first()
        if user is None:
            raise ValidationError('You are not a registered user. You must register first')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')


class DeleteForm(FlaskForm):
    delete = SubmitField('Delete')    