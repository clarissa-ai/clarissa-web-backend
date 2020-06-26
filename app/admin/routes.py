from __future__ import absolute_import

import os
import datetime
from sqlalchemy import desc

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from . import admin_bp as bp

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
    AddQuestionForm,
    EditQuestionForm,
    CreateLinkForm,
    EditLinkForm,
    CreateSummaryForm,
    EditSummaryForm,
    CreateInfoGroupForm,
    AddOptionForm,
    EditOptionForm
)

from ..main import db
from ..main.model.user import AdminUser
from ..main.model.survey import (
    Survey,
    Question,
    Link,
    Summary,
    SummaryInfoGroup,
    SummaryDetail,
    Option,
    Response
)
from ..main.model.action import Action

from .utilities import get_system_stats


# Utility function for recording admin actions
def record_action(text, type):
    a = Action(
        user_id=current_user.id,
        datetime=datetime.datetime.utcnow(),
        text=text,
        type=type
    )
    db.session.add(a)
    db.session.commit()


# Setting https redirect patterns based on environment
external = True
scheme = 'http'
if os.environ.get('DEPLOY_ENV') == 'PRODUCTION':
    scheme = 'https'


@bp.route('/sys_stats')
def sys_stats():
    return get_system_stats()


@bp.route('/')
@login_required
def index():
    return render_template(
        'dashboard/index.html',
        title="Admin Home",
        actions=Action.query.order_by(Action.id.desc()).limit(10)
    )


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("User is already logged in.")
        return redirect(url_for(
            'admin.index',
            _external=external,
            _scheme=scheme
        ))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = AdminUser.query.filter_by(email=login_form.email.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect(url_for(
                'admin.login',
                _external=external,
                _scheme=scheme))
        login_user(user, remember=login_form.remember_me.data)
        flash("Successfully logged into admin dashboard!")
        record_action("{} logged in.".format(current_user.username), "login")
        return redirect(url_for(
            "admin.index",
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        'user/login.html',
        title="Admin Login",
        form=login_form
    )


@bp.route('/logout')
def logout():
    record_action("{} logged out.".format(current_user.username), "login")
    logout_user()
    return redirect(url_for(
        'admin.index',
        _external=external,
        _scheme=scheme
    ))


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


# ------------------------------------------------------------------ #
#                          SURVEY ROUTES                             #
#   creating and editing surveys, along with questions and options   #
# ------------------------------------------------------------------ #


@bp.route('/surveys')
@login_required
def survey_home():
    active_surveys = filter(
        lambda s: not s.main, Survey.query.filter_by(active=True).all()
    )
    main_survey = Survey.query.filter_by(main=True).first()
    recent_surveys = Survey.query.order_by(desc('created_on')).limit(10)
    return render_template(
        'tools/survey/survey.html',
        title="Survey Dashboard",
        active_surveys=active_surveys,
        recent_surveys=recent_surveys,
        main_survey=main_survey
    )


@bp.route('/surveys/list')
@login_required
def all_surveys():
    page = request.args.get('page', 1, type=int)
    survey_query = Survey.query
    surveys = survey_query.paginate(page, 20)
    next_url = url_for(
        'all_surveys',
        page=surveys.next_num,
        _external=external,
        _scheme=scheme
    ) if surveys.has_next else None
    prev_url = url_for(
        'all_surveys',
        page=surveys.prev_num,
        _external=external,
        _scheme=scheme
    ) if surveys.has_prev else None
    return render_template(
        'tools/survey/list.html',
        title="Survey List",
        surveys=surveys.items,
        next_url=next_url,
        prev_url=prev_url
    )


@bp.route('/surveys/list/responses')
@login_required
def all_responses():
    page = request.args.get('page', 1, type=int)
    response_query = Response.query
    responses = response_query.paginate(page, 20)
    next_url = url_for(
        'all_surveys',
        page=responses.next_num,
        _external=external,
        _scheme=scheme
    ) if responses.has_next else None
    prev_url = url_for(
        'all_surveys',
        page=responses.prev_num,
        _external=external,
        _scheme=scheme
    ) if responses.has_prev else None
    return render_template(
        'tools/survey/list_responses.html',
        title="Survey Responses",
        responses=responses.items,
        next_url=next_url,
        prev_url=prev_url
    )


@bp.route('/surveys/new', methods=['GET', 'POST'])
@login_required
def create_survey():
    create_survey_form = CreateSurveyForm()
    if create_survey_form.validate_on_submit():

        expiration_date_datetime = datetime.datetime.strptime(
            create_survey_form.expiration_date.data, "%b %d, %Y %I:%M %p"
        )
        s = Survey(
            author_id=current_user.id,
            created_on=datetime.datetime.utcnow(),
            title=create_survey_form.title.data,
            description=create_survey_form.description.data,
            active=create_survey_form.active.data,
            expiration_date=expiration_date_datetime
        )
        db.session.add(s)
        db.session.commit()
        # IMAGE UPLOADING LOGIC
        if create_survey_form.image_upload.data:
            f = create_survey_form.image_upload.data
            s.image_file = f.read()
            s.image_type = f.filename.split(".")[-1]
            db.session.add(s)
            db.session.commit()

        if create_survey_form.main.data:
            main_s = Survey.query.filter_by(main=True).first()
            if main_s:
                flash(
                    "Failed to publish main survey: Main survey \"{}\" \
                    already exists.".format(s.title)
                )
            else:
                s.main = True
                s.active = True
        db.session.add(s)
        db.session.commit()
        record_action(
            "\"{}\" survey created (id: {})".format(s.title, s.id),
            "create"
        )
        return redirect(url_for(
            'admin.survey_view',
            id=s.id,
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        'tools/survey/new.html',
        title="New Survey",
        form=create_survey_form
    )


@bp.route('/survey/<survey_id>/link/new', methods=['GET', 'POST'])
@login_required
def create_link(survey_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    if len(s.links) == 4:
        flash('No more than 4 links are allowed per survey.')
        return redirect(url_for(
            'admin.survey_view',
            id=s.id,
            _external=external,
            _scheme=scheme
        ))
    create_link_form = CreateLinkForm()
    if create_link_form.validate_on_submit():
        link = Link(
            title=create_link_form.title.data,
            description=create_link_form.description.data,
            link=create_link_form.link.data,
            survey_id=s.id
        )
        db.session.add(link)
        db.session.commit()

        # IMAGE UPLOADING LOGIC
        if create_link_form.image_upload.data:
            f = create_link_form.image_upload.data
            link.image_file = f.read()
            link.image_type = f.filename.split(".")[-1]

        db.session.add(link)
        db.session.commit()
        record_action("Added link {} to survey \"{}\".".format(
            link.title,
            link.survey.title),
            "create"
        )
        return redirect(url_for(
            'admin.survey_view',
            id=s.id,
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        'tools/survey/new_link.html',
        title="Create a new link",
        form=create_link_form,
        survey=s
    )


@bp.route('/survey/<survey_id>/link/edit/<link_id>', methods=['GET', 'POST'])
@login_required
def edit_link(survey_id, link_id):
    s = Survey.query.filter_by(id=survey_id).first()
    link = Link.query.filter_by(id=link_id).first()
    if not s or not link:
        flash("Requested item doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    edit_link_form = EditLinkForm()
    if edit_link_form.validate_on_submit():
        link.title = edit_link_form.title.data
        link.description = edit_link_form.description.data
        link.link = edit_link_form.link.data

        # IMAGE UPLOADING LOGIC
        if edit_link_form.image_upload.data:
            f = edit_link_form.image_upload.data
            link.image_file = f.read()
            link.image_type = f.filename.split(".")[-1]

        db.session.add(link)
        db.session.commit()
        record_action("Edited link {} in survey \"{}\".".format(
            link.title,
            link.survey.title),
            "edit"
        )
        return redirect(url_for(
            'admin.survey_view',
            id=s.id,
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        'tools/survey/edit_link.html',
        title="Editing link",
        form=edit_link_form,
        survey=s,
        link=link
    )


@login_required
@bp.route('/survey/<survey_id>/link/<link_id>/delete')
def delete_link(survey_id, link_id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    link = Link.query.filter_by(id=link_id).first()
    if not link:
        flash("Requested link doesn't exist.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    db.session.delete(link)
    db.session.commit()
    record_action(
        "Deleted link {} from survey \"{}\".".format(
            link.title,
            link.survey.title
        ),
        "destroy"
    )
    return redirect(url_for(
        'admin.survey_view',
        id=survey_id,
        _external=external,
        _scheme=scheme
    ))


@bp.route('/survey/<id>')
@login_required
def survey_view(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    root = Question.query.filter_by(id=s.root_id).first()
    return render_template(
        'tools/survey/view.html',
        title="Survey: {}".format(s.title),
        survey=s,
        root=root
    )


@bp.route('/survey/<id>/deactivate')
@login_required
def deactivate_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    if s.main:
        s.main = False
    s.active = False
    db.session.add(s)
    db.session.commit()
    record_action("Deactivated survey \"{}\".".format(s.title), "destroy")
    return redirect(url_for(
        'admin.survey_view',
        id=s.id,
        _external=external,
        _scheme=scheme
    ))


@bp.route('/survey/<id>/activate')
@login_required
def activate_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    s.active = True
    db.session.add(s)
    db.session.commit()
    record_action("Activated survey \"{}\".".format(s.title), "create")
    return redirect(url_for(
        'admin.survey_view',
        id=s.id,
        _external=external,
        _scheme=scheme
    ))


@bp.route('/survey/<id>/pub_main_survey')
@login_required
def pub_main_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    main_survey = Survey.query.filter_by(main=True).first()
    if main_survey:
        main_survey.main = False
    s.main = True
    s.active = True
    db.session.add(s)
    db.session.commit()
    record_action("Published survey \"{}\".".format(s.title), "create")
    return redirect(url_for(
        'admin.survey_view',
        id=s.id,
        _external=external,
        _scheme=scheme
    ))


@bp.route('/survey/<id>/depub_main_survey')
@login_required
def depub_main_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    s.main = False
    db.session.add(s)
    db.session.commit()
    record_action("Unpublished survey \"{}\".".format(s.title), "destroy")
    return redirect(url_for(
        'admin.survey_view',
        id=s.id,
        _external=external,
        _scheme=scheme
    ))


@bp.route('/surveys/new/<survey_id>/question', methods=['GET', 'POST'])
@login_required
def add_question(survey_id):
    root = request.args.get('root')
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))

    add_question_form = AddQuestionForm(s.questions)
    if add_question_form.validate_on_submit():
        q = Question(
            title=add_question_form.title.data,
            description=add_question_form.description.data,
            type=add_question_form.type.data,
            survey_id=survey_id,
            default_next_id=add_question_form.default_next.data
        )
        db.session.add(q)
        db.session.commit()
        if add_question_form.root.data:
            s.root_id = q.id
        db.session.add(s)
        db.session.commit()
        record_action(
            "Added question \"{}\" to survey \"{}\".".format(q.title, s.title),
            "create"
        )
        return redirect(
            url_for(
                'admin.question_view',
                survey_id=s.id,
                question_id=q.id,
                _external=external,
                _scheme=scheme
            )
        )
    return render_template(
        'tools/survey/new_question.html',
        title="New Question",
        form=add_question_form,
        survey=s,
        root=root
    )


@login_required
@bp.route('/survey/<survey_id>/question/<question_id>')
def question_view(survey_id, question_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question doesn't exist.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    d_n = Question.query.filter_by(id=q.default_next_id).first()
    if d_n:
        q.default_next_title = d_n.title
        q.default_next_link = url_for(
            'admin.question_view',
            survey_id=s.id,
            question_id=d_n.id,
            _external=external,
            _scheme=scheme
        )
    else:
        q.default_next_title = "Final Question (directs to summary)"
        q.default_next_link = ""
    option_data = {}
    for option in q.options:
        next_q = Question.query.filter_by(id=option.next_id).first()
        option_data[option.id] = {}
        option_data[option.id]["next_link"] = url_for(
                "admin.question_view",
                survey_id=option.question.survey.id,
                question_id=option.next_id,
                _external=external,
                _scheme=scheme
            ) if next_q else url_for(
                "admin.question_view",
                survey_id=option.question.survey.id,
                question_id=option.question.default_next_id,
                _external=external,
                _scheme=scheme
            )
        if next_q:
            option_data[option.id]["next_title"] = next_q.title
        elif option.next_id == -1:
            option_data[option.id]["next_title"] = "Direct to summary"
        else:
            option_data[option.id]["next_title"] = ("No next question assigned"
                                                    " (uses default next)")
        option_summary = Summary.query.filter_by(id=option.summary_id).first()
        option_data[option.id]["summary_link"] = url_for(
            'admin.view_summary',
            survey_id=option.question.survey.id,
            summary_id=option_summary.id,
            _external=external,
            _scheme=scheme
        ) if option_summary else ""
        option_data[option.id]["summary_title"] = option_summary.title or "No \
            associated summary exists"
    return render_template(
        'tools/survey/view_question.html',
        title="Question: {}".format(q.title),
        question=q,
        option_data=option_data
    )


@bp.route(
    '/surveys/new/<survey_id>/question/<question_id>/option',
    methods=['GET', 'POST']
)
@login_required
def add_option(survey_id, question_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question doesn't exist.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    # vvv THIS WHOLE SECTION CAN BE OPTIMIZED WITH ANOTHER SQL QUERY vvv
    questions = []
    for sq in s.questions:
        if sq.id != q.id:
            questions.append(sq)
    add_option_form = AddOptionForm(questions, s.summaries)
    if add_option_form.validate_on_submit():
        o = Option(
            title=add_option_form.title.data,
            question_id=q.id
        )
        if add_option_form.next_question.data:
            if add_option_form.next_question.data != -2:
                o.next_id = add_option_form.next_question.data
        if add_option_form.summary.data:
            o.summary_id = add_option_form.summary.data
            if add_option_form.summary_weight.data:
                o.summary_weight = add_option_form.summary_weight.data
        db.session.add(o)
        db.session.commit()
        return redirect(url_for(
            'admin.question_view',
            survey_id=s.id,
            question_id=q.id,
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        '/tools/survey/new_option.html',
        title="New Option",
        form=add_option_form,
        survey=s,
        question=q
    )


@bp.route(
    '/survey/edit/<survey_id>/question/<question_id>/delete_option/<option_id>'
)
@login_required
def delete_option(survey_id, question_id, option_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    o = Option.query.filter_by(id=option_id).first()
    if not o:
        flash("Requested option could not be found in database.")
        return redirect(url_for(
            'admin.question_view',
            survey_id=survey_id,
            question_id=question_id,
            _external=external,
            _scheme=scheme
        ))
    db.session.delete(o)
    db.session.commit()
    return redirect(url_for(
        'admin.question_view',
        survey_id=survey_id,
        question_id=question_id,
        _external=external,
        _scheme=scheme
    ))


@bp.route('/surveys/edit/<survey_id>', methods=['GET', 'POST'])
@login_required
def edit_survey(survey_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    edit_survey_form = EditSurveyForm()
    if edit_survey_form.validate_on_submit():
        expiration_date_datetime = datetime.datetime.strptime(
            edit_survey_form.expiration_date.data, "%b %d, %Y %I:%M %p"
        )
        s.title = edit_survey_form.title.data
        s.description = edit_survey_form.description.data
        s.active = edit_survey_form.active.data
        s.expiration_date = expiration_date_datetime

        # IMAGE UPLOADING LOGIC
        if edit_survey_form.image_upload.data:
            f = edit_survey_form.image_upload.data
            s.image_file = f.read()
            s.image_type = f.filename.split(".")[-1]

        db.session.add(s)
        db.session.commit()
        record_action("Edited survey \"{}\".".format(s.title), "edit")
        return redirect(url_for(
            'admin.survey_view',
            id=s.id,
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        'tools/survey/edit.html',
        title="Edit Survey",
        form=edit_survey_form,
        survey=s
    )


@bp.route(
    '/surveys/edit/<survey_id>/question/<question_id>',
    methods=['GET', 'POST']
)
@login_required
def edit_question(survey_id, question_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    edit_question_form = EditQuestionForm(
        Question.query.filter_by(survey_id=survey_id).filter(
            Question.id != question_id
        ).all()
    )
    if edit_question_form.validate_on_submit():
        q.title = edit_question_form.title.data
        q.description = edit_question_form.description.data
        q.type = edit_question_form.type.data
        if edit_question_form.root.data:
            s.root_id = q.id
        q.default_next_id = edit_question_form.default_next.data
        db.session.add(s)
        db.session.add(q)
        db.session.commit()
        record_action("Edited question \"{}\" in survey \"{}\".".format(
            q.title, q.survey.title),
            "edit"
        )
        back_link = request.args.get('back_link')
        return redirect(
            url_for(
                'admin.survey_view',
                id=s.id,
                _external=external,
                _scheme=scheme
            )
        ) if not back_link else redirect(back_link)
    edit_question_form.type.data = q.type
    edit_question_form.default_next.data = q.default_next_id
    return render_template(
        'tools/survey/edit_question.html',
        title="Edit Question",
        form=edit_question_form,
        question=q,
        survey=s
    )


@bp.route('/surveys/edit/<survey_id>/delete_question/<question_id>')
@login_required
def delete_question(survey_id, question_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    db.session.delete(q)
    db.session.commit()
    record_action(
        "Deleted question \"{}\" from survey \"{}\".".format(
            q.title,
            q.survey.title
        ),
        "destroy"
    )
    return redirect(url_for(
        'admin.survey_view',
        id=survey_id,
        _external=external,
        _scheme=scheme
    ))


@bp.route(
    '/surveys/edit/<survey_id>/question/<question_id>/option/<option_id>',
    methods=['GET', 'POST']
)
@login_required
def edit_option(survey_id, question_id, option_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    o = Option.query.filter_by(id=option_id).first()
    if not o:
        flash("Requested option could not be found in database.")
        return redirect(url_for(
            'admin.question_view',
            survey_id=survey_id,
            question_id=question_id,
            _external=external,
            _scheme=scheme
        ))
    edit_option_form = EditOptionForm(
        Question.query.filter(Question.survey_id == survey_id).filter(
            Question.id != question_id
        ).all(),
        s.summaries
    )
    if edit_option_form.validate_on_submit():
        o.title = edit_option_form.title.data
        if not edit_option_form.next_question.data == -2:
            o.next_id = edit_option_form.next_question.data
        else:
            o.next_id = None
        o.summary_id = edit_option_form.summary.data
        if edit_option_form.summary_weight.data != 0:
            o.summary_weight = edit_option_form.summary_weight.data
        db.session.add(o)
        db.session.commit()
        return redirect(url_for(
            'admin.question_view',
            survey_id=survey_id,
            question_id=question_id,
            _external=external,
            _scheme=scheme
        ))
    edit_option_form.summary.data = o.summary_id
    edit_option_form.next_question.data = o.next_id
    return render_template(
        '/tools/survey/edit_option.html',
        form=edit_option_form,
        question=q,
        survey=s,
        option=o
    )


@bp.route('/surveys/<survey_id>/create_summary', methods=['GET', 'POST'])
@login_required
def create_summary(survey_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    form = CreateSummaryForm()
    if form.validate_on_submit():
        summary = Summary(
            title=form.title.data,
            description=form.description.data,
            survey_id=survey_id
        )
        db.session.add(summary)
        db.session.commit()

        # IMAGE UPLOADING LOGIC
        if form.image_upload.data:
            f = form.image_upload.data
            summary.image_file = f.read()
            summary.image_type = f.filename.split(".")[-1]

        db.session.add(summary)
        db.session.commit()

        record_action(
            "Added summary \"{}\" to survey \"{}\".".format(
                summary.title,
                summary.survey.title
            ),
            "create"
        )
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        '/tools/survey/new_summary.html',
        title="Creating Summary",
        form=form,
        survey=s
    )


@bp.route(
    '/surveys/<survey_id>/view_summary/<summary_id>',
    methods=['GET', 'POST']
)
@login_required
def view_summary(survey_id, summary_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        '/tools/survey/view_summary.html',
        title="Viewing summary",
        summary=summary,
        survey=survey
    )


@bp.route(
    '/surveys/<survey_id>/edit_summary/<summary_id>',
    methods=['GET', 'POST']
)
@login_required
def edit_summary(survey_id, summary_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    form = EditSummaryForm()
    if form.validate_on_submit():
        summary.title = form.title.data
        summary.description = form.description.data

        # IMAGE UPLOADING LOGIC
        if form.image_upload.data:
            f = form.image_upload.data
            summary.image_file = f.read()
            summary.image_type = f.filename.split(".")[-1]

        db.session.add(summary)
        db.session.commit()
        record_action(
            "Edited summary \"{}\" in survey \"{}\".".format(
                summary.title,
                summary.survey.title
            ),
            "edit"
        )
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    return render_template(
        '/tools/survey/edit_summary.html',
        survey=s,
        summary=summary,
        form=form
    )


@bp.route(
    '/surveys/<survey_id>/delete_summary/<summary_id>',
    methods=['GET', 'POST']
)
@login_required
def delete_summary(survey_id, summary_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    db.session.delete(summary)
    db.session.commit()
    record_action(
        "Deleted summary \"{}\" from survey \"{}\".".format(
            summary.title,
            summary.survey.title
        ),
        "destroy"
    )
    return redirect(url_for(
        'admin.survey_view',
        id=survey_id,
        _external=external,
        _scheme=scheme
    ))


@bp.route(
    '/surveys/<survey_id>/summary/<summary_id>/new_info_group',
    methods=['GET', 'POST']
)
@login_required
def create_info_group(survey_id, summary_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    form = CreateInfoGroupForm()

    # Complex form logic
    if form.validate_on_submit():
        g = SummaryInfoGroup(
            title=form.title.data,
            link_URL=form.link.data,
            summary_id=summary_id
        )
        db.session.add(g)
        db.session.commit()
        for detail in form.details.data:
            d = SummaryDetail(text=detail['text'], infogroup_id=g.id)
            db.session.add(d)
        db.session.commit()
        record_action(
            "Added info group \"{}\" to summary \"{}\".".format(
                g.title,
                g.summary.title
            ),
            "create"
        )
        return redirect(url_for(
            'admin.view_summary',
            survey_id=survey_id,
            summary_id=summary_id,
            _external=external,
            _scheme=scheme
        ))

    return render_template(
        '/tools/survey/new_info_group.html',
        title="Create Summary Information Group",
        form=form,
        survey=survey,
        summary=summary
    )


@bp.route(
    '/surveys/<survey_id>/summary/<summary_id>/infogroup/<infogroup_id>/delete'
)
@login_required
def delete_info_group(survey_id, summary_id, infogroup_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        flash("Requested survey doesn't exist.")
        return redirect(url_for(
            'admin.survey_home',
            _external=external,
            _scheme=scheme
        ))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for(
            'admin.survey_view',
            id=survey_id,
            _external=external,
            _scheme=scheme
        ))
    infogroup = SummaryInfoGroup.query.filter_by(id=infogroup_id).first()
    if not infogroup:
        flash("Requested info group doesn't exist.")
        return redirect(url_for(
            'admin.view_summary',
            survey_id=survey.id,
            summary_id=summary.id,
            _external=external,
            _scheme=scheme
        ))
    db.session.delete(infogroup)
    db.session.commit()
    record_action(
        "Deleted info group \"{}\" from summary \"{}\".".format(
            infogroup.title,
            infogroup.summary.title
        ),
        "create"
    )
    return redirect(url_for(
        'admin.view_summary',
        survey_id=survey.id,
        summary_id=summary.id,
        _external=external,
        _scheme=scheme
    ))


@bp.route('/surveys/survey_design_guide/<survey_id>/<survey_title>')
@login_required
def survey_design_guide(survey_id, survey_title):
    return render_template(
        '/tools/survey/survey_design_guide.html',
        title="Survey Design Guide",
        survey_id=survey_id,
        survey_title=survey_title
    )


# ---------------------------------------------------------------- #
#                   CUSTOM ROUTE SETTING ROUTES                    #
#           Configure custom routes for frontend pull              #
# ---------------------------------------------------------------- #

@bp.route('/custom_routes')
@login_required
def routes_home():
    return render_template(
        '/tools/route/home.html',
        title='Custom Routing'
    )


# ---------------------------------------------------------------- #
#               DEVELOPMENT ADMINISTRATION ROUTES                  #
#            get status of git repos and deployments               #
# ---------------------------------------------------------------- #

@bp.route('/development')
@login_required
def development_home():
    return render_template('tools/dev/home.html', title="Dev Dashboard")


# ---------------------------------------------------------------- #
#                    USER ADMINISTRATION ROUTES                    #
#           Configure administrative user privelleges              #
# ---------------------------------------------------------------- #

@bp.route('/user_list')
@login_required
def user_list():
    return render_template(
        'dashboard/administration/user_list.html',
        title="Admin User List"
    )
