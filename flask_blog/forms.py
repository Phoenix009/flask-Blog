from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from flask_blog.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min = 2, max = 20)])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired()])
    submit = SubmitField('SignUp')

    # Custom Validators
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("Username is already taken")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("Account with that email already exists")



class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("LogIn")



class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min = 2, max = 20)])
    email = StringField("Email", validators=[InputRequired(), Email()])
    picture = FileField("Update Profile Pic", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField('Update')

    # Custom Validators
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError("Username is already taken")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError("Account with that email already exists")




class PostForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Content", validators=[InputRequired()])
    submit = SubmitField("Post")




