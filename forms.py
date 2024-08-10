from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, StringField, DateField, PasswordField, FieldList, FormField
from wtforms.validators import DataRequired,Email

class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Log in")

class RegistrationForm(FlaskForm):
    username = StringField('Username' ,validators=[DataRequired()])
    email = StringField('Email' , validators=[DataRequired(),Email()])
    password = StringField('Username', validators=[DataRequired()])
    submit = SubmitField("Register")