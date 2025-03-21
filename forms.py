from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Length
from wtforms import FieldList, FormField, TimeField, DateField, IntegerField, SelectField, TextAreaField

class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(3,20)])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Log in')

class RegisterForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(3,20)])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired()])
    submit=SubmitField('Register')

class ActivityForm(FlaskForm):
    details = StringField("Activity Details", validators=[DataRequired(message="This field is required.")])
    start_time = TimeField("Start Time", validators=[DataRequired(message="This field is required.")])
    end_time = TimeField("End Time", validators=[DataRequired(message="This field is required.")])

class ActivityListForm(FlaskForm):
    activities = FieldList(
        FormField(ActivityForm),
        min_entries=1,
        validators=[DataRequired(message="At least one activity is required.")]
    )
    submit = SubmitField("Save Activities")

class GoalForm(FlaskForm):
    details = StringField('Goal Details', validators=[DataRequired()])
    hour_goal = IntegerField('Hour Goal (Optional)')
    month = StringField('Month', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])

