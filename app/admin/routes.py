from __future__ import absolute_import

from flask import (
    render_template, 
    redirect, 
    url_for,
    flash
)

from . import bp 

from flask_login import (
    login_required, 
    current_user, 
    login_user,
    logout_user
)

from .forms import LoginForm

from ..main.model.user import User

@bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', title="Admin Home")



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("User is already logged in.")
        return redirect(url_for('admin.index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('admin.login'))
        login_user(user, remember=login_form.remember_me.data)
        flash("Successfully logged into admin dashboard!")
        return redirect(url_for("admin.index"))
    return render_template('auth/login.html', title="Admin Login", form=login_form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', title="Admin Dashboard")


#---------------------------------------------------------------------------------------------#
#     SURVEY ROUTES: creating and editing surveys, along with questions and options           #
#---------------------------------------------------------------------------------------------#

@bp.route('/surveys')
@login_required
def survey_home():
    return render_template('tools/survey/survey.html', title="Survey Dashboard")

@bp.route('/surveys/new')
@login_required
def create_survey():
    create_survey_form = CreateSurveyForm()
    return render_template('tools/survey/new.html', title="New Survey", form=create_survey_form)

@bp.route('/surveys/new/<survey_id>/question')
@login_required
def add_question(survey_id):
    add_question_form = AddQuestionForm()
    return render_template('tools/survey/new_question.html', title="New Question", form=add_question_form)

@bp.route('/surveys/new/<survey_id>/question/<question_id>/option')
def add_option(survey_id, question_id):
    add_option_form = AddOptionForm()
    return render_template('/tools/survey/new_option.html', title="New Option", form=add_option_form)

@bp.route('/surveys/edit/<survey_id>')
@login_required
def edit_survey(survey_id):
    edit_survey_form = EditSurveyForm()
    return render_template('tools/survey/edit.html', title="Edit Survey")

@bp.route('/surveys/edit/<survey_id>/question')
@login_required
def edit_question(survey_id):
    edit_question_form = EditQuestionForm()
    return render_template('tools/survey/edit_question.html', title="Edit Question")

@bp.route('/surveys/edit/<survey_id>/question/<question_id>/option')
def edit_option(survey_id, question_id):
    edit_option_form = EditOptionForm()
    return render_template('/tools/survey/edit_option.html')

