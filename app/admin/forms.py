from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    PasswordField, 
    BooleanField, 
    SubmitField, 
    TextAreaField,
    SelectField
)
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class CreateAdminAccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])

class CreateSurveyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    active = BooleanField('Active')
    expiration_date = StringField('Expiration date', validators=[DataRequired()])
    submit = SubmitField("Create Survey")

class EditSurveyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    active = BooleanField('Active')
    expiration_date = StringField('Expiration date', validators=[DataRequired()])
    submit = SubmitField("Confirm Changes")

class AddQuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], choices=[('multiple_choice', 'Multiple Choice'),])
    root = BooleanField('Root')
    submit = SubmitField("Add Question to Survey")
    
class EditQuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], choices=[('multiple_choice', 'Multiple Choice'),])
    root = BooleanField('Root')
    submit = SubmitField("Add Question to Survey")
