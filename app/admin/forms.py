from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed  # , FileRequired
from wtforms import (
    Form,
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    SelectField,
    FieldList,
    FormField,
    IntegerField
)
from wtforms.validators import DataRequired
from ..main.model.survey import Question


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
    image_upload = FileField(
        'Title Image',
        validators=[FileAllowed(['jpg', 'png'], 'Images only!')]
    )
    cover_image_upload = FileField(
        'Cover Image',
        validators=[FileAllowed(['jpg', 'png'], 'Images only!')]
    )
    active = BooleanField('Active')
    main = BooleanField('Main')
    expiration_date = StringField(
        'Expiration date',
        validators=[DataRequired()]
    )
    submit = SubmitField("Create Survey")


class EditSurveyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_upload = FileField(
        'Title Image',
        validators=[FileAllowed(['jpg', 'png'], 'Images only!')]
    )
    cover_image_upload = FileField(
        'Cover Image',
        validators=[FileAllowed(['jpg', 'png'], 'Images only!')]
    )
    active = BooleanField('Active')
    expiration_date = StringField(
        'Expiration date',
        validators=[DataRequired()]
    )
    submit = SubmitField("Confirm Changes")


class AddQuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField(
        'Type',
        validators=[DataRequired()],
        choices=Question.get_type_list()
    )
    default_next = SelectField(
        'Default Next Question',
        validators=[DataRequired()],
        coerce=int,
        choices=[]
    )
    root = BooleanField('Root')
    submit = SubmitField("Add Question to Survey")

    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_next.choices = [(q.id, q.title) for q in questions]
        self.default_next.choices.insert(
            0, (-1, 'Last Question (Direct to summary)')
        )


class EditQuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField(
        'Type',
        validators=[DataRequired()],
        choices=Question.get_type_list()
    )
    default_next = SelectField(
        'Default Next Question',
        validators=[DataRequired()],
        coerce=int,
        choices=[]
    )
    root = BooleanField('Root')
    submit = SubmitField("Confirm Changes")

    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_next.choices = [(q.id, q.title) for q in questions]
        self.default_next.choices.insert(
            0, (-1, 'Last Question (Direct to summary)')
        )


class CreateLinkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    link = StringField('Link URL', validators=[DataRequired()])
    image_upload = FileField(
        'Link Image',
        validators=[FileAllowed(['jpg', 'png'], 'Images only!')]
    )
    submit = SubmitField('Add Link to Survey')


class EditLinkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    link = StringField('Link URL', validators=[DataRequired()])
    image_upload = FileField(
        'Link Image',
        validators=[FileAllowed(['jpg', 'png'], 'Images only!')]
    )
    submit = SubmitField('Confirm Changes')


class CreateSummaryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_upload = FileField(
        'Link Image',
        validators=[FileAllowed(['jpg', 'png'], 'Images only!')]
    )
    submit = SubmitField('Add Summary to Survey')


class EditSummaryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_upload = FileField(
        'Link Image',
        validators=[FileAllowed(['jpg', 'png'], 'Images only!')]
    )
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


class AddOptionForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired()])
    next_question = SelectField('Next Question', choices=[], coerce=int)
    summary = SelectField('Summary', choices=[], coerce=int)
    summary_weight = IntegerField('Summary weight')
    submit = SubmitField('Add Option')

    def __init__(self, questions, summaries, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_question.choices = [(q.id, q.title) for q in questions]
        self.next_question.choices.insert(
            0, (-1, 'Last Question (Direct to summary)')
        )
        self.next_question.choices.insert(
            0, (-2, 'Use Question\'s Default Next')
        )
        self.summary.choices = [(s.id, s.title) for s in summaries]
        self.summary.choices.insert(0, (0, "None"))


class EditOptionForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired()])
    next_question = SelectField('Next Question', choices=[], coerce=int)
    summary = SelectField('Summary', choices=[], coerce=int)
    summary_weight = IntegerField('Summary weight')
    submit = SubmitField('Confirm Changes')

    def __init__(self, questions, summaries, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_question.choices = [(q.id, q.title) for q in questions]
        self.next_question.choices.insert(
            0, (-1, 'Last Question (Direct to summary)')
        )
        self.next_question.choices.insert(
            0, (-2, 'Use Question\'s Default Next')
        )
        self.summary.choices = [(s.id, s.title) for s in summaries]
        self.summary.choices.insert(0, (0, "None"))


class CreateRouteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    origin = StringField(
        'Origin (user requested URL)',
        validators=[DataRequired()]
    )
    target = StringField(
        'Target (redirected URL)',
        validators=[DataRequired()]
    )
    active = BooleanField('Active')
    submit = SubmitField('Create Route')


class EditRouteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    origin = StringField(
        'Origin (user requested URL)',
        validators=[DataRequired()]
    )
    target = StringField(
        'Target (redirected URL)',
        validators=[DataRequired()]
    )
    active = BooleanField('Active')
    submit = SubmitField('Confirm Changes')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Confirm Changes')


class EditPasswordForm(FlaskForm):
    current_password = PasswordField(
        'Enter Current Password',
        validators=[DataRequired()]
    )
    new_password = PasswordField(
        'Enter New Password',
        validators=[DataRequired()]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired()]
    )
    submit = SubmitField('Confirm Changes')


class CreateAdminUser(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    submit = SubmitField('Create New User')
