from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Length

class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(3,20)])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Log in')

class RegisterForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(3,20)])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Register')
    
