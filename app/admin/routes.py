from __future__ import absolute_import
import datetime

from flask import (
    render_template, 
    redirect, 
    url_for,
    flash,
    request
)

from . import bp 

from flask_login import (
    login_required, 
    current_user, 
    login_user,
    logout_user
)

from .forms import (
    LoginForm, 
    CreateSurveyForm,
    EditSurveyForm,
    AddQuestionForm
)

from ..main import db
from ..main.model.user import User
from ..main.model.survey import Survey, Question

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
        if user.admin == True:
            login_user(user, remember=login_form.remember_me.data)
            flash("Successfully logged into admin dashboard!")
            return redirect(url_for("admin.index"))
        else:
            flash("User does not have administrative privelleges.")
    return render_template('user/login.html', title="Admin Login", form=login_form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', title="Admin Dashboard")

@bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')

@bp.route('/profile/edit')
@login_required
def edit_profile():
    return render_template('user/settings.html')

#---------------------------------------------------------------------------------------------#
#     SURVEY ROUTES: creating and editing surveys, along with questions and options           #
#---------------------------------------------------------------------------------------------#

@bp.route('/surveys')
@login_required
def survey_home():
    active_surveys = Survey.query.filter_by(active=True).all()
    recent_surveys = Survey.query.order_by('updated desc').limit(10)
    return render_template('tools/survey/survey.html', 
                            title="Survey Dashboard", 
                            active_surveys=active_surveys, 
                            recent_surveys=recent_surveys)
@bp.route('/surveys/list')
@login_required
def all_surveys():
    return render_template('tools/survey/list.html')

@bp.route('/surveys/new', methods=['GET','POST'])
@login_required
def create_survey():
    create_survey_form = CreateSurveyForm()
    if create_survey_form.validate_on_submit():
        expiration_date_datetime = datetime.datetime.strptime(create_survey_form.expiration_date.data, "%b %d, %Y %I:%M %p")
        s = Survey(
            author_id = current_user.id,
            created_on = datetime.datetime.utcnow(),
            title = create_survey_form.title.data,
            description = create_survey_form.description.data,
            active = create_survey_form.active.data,
            expiration_date = expiration_date_datetime
        )
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('admin.survey_view', id=s.id))
    return render_template('tools/survey/new.html', title="New Survey", form=create_survey_form)

@bp.route('/survey/<id>')
@login_required
def survey_view(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    return render_template('tools/survey/view.html', title="Survey: {}".format(s.title), survey=s)

@bp.route('/survey/<id>/deactivate')
@login_required
def deactivate_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    s.active = False
    db.session.add(s)
    db.session.commit()
    return redirect(url_for('admin.survey_view', id=s.id))

@bp.route('/survey/<id>/activate')
@login_required
def activate_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    s.active = True
    db.session.add(s)
    db.session.commit()
    return redirect(url_for('admin.survey_view', id=s.id))

@bp.route('/surveys/new/<survey_id>/question', methods=['GET', 'POST'])
@login_required
def add_question(survey_id):
    root = request.args.get('root')
    add_question_form = AddQuestionForm()
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    if add_question_form.validate_on_submit():
        q = Question(
            title=add_question_form.title.data,
            description=add_question_form.description.data,
            type=add_question_form.type.data
        )
        if add_question_form.root.data:
            s.root = None
            db.session.add(s)
            s.root = q
        q.survey_id = s.id
        db.session.add(s)
        db.session.add(q)
        db.session.commit()
        return redirect(url_for('admin.question_view', survey_id=s.id, question_id=q.id))
    return render_template('tools/survey/new_question.html', title="New Question", form=add_question_form, survey=s, root=root)

@login_required
@bp.route('/survey/<survey_id>/question/<question_id>')
def question_view(survey_id, question_id):
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    return render_template('tools/survey/view_question.html', title="Question: {}".format(q.title), question=q)

@bp.route('/surveys/new/<survey_id>/question/<question_id>/option')
@login_required
def add_option(survey_id, question_id):
    add_option_form = AddOptionForm()
    return render_template('/tools/survey/new_option.html', title="New Option", form=add_option_form)

@bp.route('/surveys/edit/<survey_id>', methods=['GET', 'POST'])
@login_required
def edit_survey(survey_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    edit_survey_form = EditSurveyForm()
    if edit_survey_form.validate_on_submit():
        expiration_date_datetime = datetime.datetime.strptime(edit_survey_form.expiration_date.data, "%b %d, %Y %I:%M %p")
        s.title = edit_survey_form.title.data
        s.description = edit_survey_form.description.data
        s.active = edit_survey_form.active.data
        s.expiration_date = expiration_date_datetime
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('admin.survey_view', id=s.id))
    return render_template('tools/survey/edit.html', title="Edit Survey", form=edit_survey_form, survey=s)

@bp.route('/surveys/edit/<survey_id>/question/<question_id>')
@login_required
def edit_question(survey_id, question_id):
    edit_question_form = EditQuestionForm()
    return render_template('tools/survey/edit_question.html', title="Edit Question")

@bp.route('/surveys/edit/<survey_id>/delete_question/<question_id>')
@login_required
def delete_question(survey_id, question_id):
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    db.session.delete(q)
    db.session.commit()
    return redirect(url_for('admin.survey_view', id=survey_id))

@bp.route('/surveys/edit/<survey_id>/question/<question_id>/option')
def edit_option(survey_id, question_id):
    edit_option_form = EditOptionForm()
    return render_template('/tools/survey/edit_option.html')

#---------------------------------------------------------------------------------------------#
#    DEVELOPMENT ADMINISTRATION ROUTES: get status of git repos and deployments               #
#---------------------------------------------------------------------------------------------#

@bp.route('/development')
@login_required
def development_home():
    return render_template('tools/dev/home.html', title="Dev Dashboard")