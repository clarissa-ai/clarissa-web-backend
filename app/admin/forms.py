from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    Form,
    StringField, 
    PasswordField, 
    BooleanField, 
    SubmitField, 
    TextAreaField,
    SelectField,
    FieldList, 
    FormField
)
from wtforms.validators import DataRequired

question_types = [('multiple_choice', 'Multiple Choice'),]

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
    image_upload = FileField('Title Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    active = BooleanField('Active')
    main = BooleanField('Main')
    expiration_date = StringField('Expiration date', validators=[DataRequired()])
    submit = SubmitField("Create Survey")

class EditSurveyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_upload = FileField('Title Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    active = BooleanField('Active')
    expiration_date = StringField('Expiration date', validators=[DataRequired()])
    submit = SubmitField("Confirm Changes")

class AddQuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], choices=question_types)
    root = BooleanField('Root')
    submit = SubmitField("Add Question to Survey")
    
class EditQuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], choices=question_types)
    root = BooleanField('Root')
    submit = SubmitField("Confirm Changes")

class CreateLinkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    link = StringField('Link URL', validators=[DataRequired()])
    image_upload = FileField('Link Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Add Link to Survey')

class EditLinkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    link = StringField('Link URL', validators=[DataRequired()])
    image_upload = FileField('Link Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Confirm Changes')

class CreateSummaryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_upload = FileField('Link Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Add Summary to Survey')

class EditSummaryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_upload = FileField('Link Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Confirm Changes')

class DetailForm(Form):
    text = StringField('Detail Text (bullet):')

class CreateInfoGroupForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    link = StringField('Link URL', validators=[DataRequired()])
    details = FieldList(
        FormField(DetailForm),
        min_entries=1,
        max_entries=10
    )
