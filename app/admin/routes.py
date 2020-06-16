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

from werkzeug.utils import secure_filename

from ..main import db
from ..main.model.user import AdminUser
from ..main.model.survey import (
    Survey, 
    Question, 
    Link, 
    Summary, 
    SummaryInfoGroup, 
    SummaryDetail, 
    Option
)

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
        user = AdminUser.query.filter_by(email=login_form.email.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('admin.login'))
        login_user(user, remember=login_form.remember_me.data)
        flash("Successfully logged into admin dashboard!")
        return redirect(url_for("admin.index"))
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
    active_surveys = filter(lambda s: s.main != True, Survey.query.filter_by(active=True).all())
    main_survey = Survey.query.filter_by(main=True).first()
    recent_surveys = Survey.query.order_by(desc('created_on')).limit(10)
    return render_template('tools/survey/survey.html', 
                            title="Survey Dashboard", 
                            active_surveys=active_surveys, 
                            recent_surveys=recent_surveys,
                            main_survey=main_survey)
@bp.route('/surveys/list')
@login_required
def all_surveys():
    return render_template('tools/survey/list.html')

@bp.route('/surveys/list/responses')
@login_required
def all_responses():
    return render_template('tools/survey/list_responses.html')

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
        # IMAGE UPLOADING LOGIC
        image_link = None
        if create_survey_form.image_upload.data:
            f = create_survey_form.image_upload.data
            filename = secure_filename(f.filename)
            image_link = "survey_{}_title_image_{}".format(s.id, filename)
            image_folder = os.path.abspath(os.path.dirname(__file__)) + "/../resources/images/"
            file_path = os.path.join(image_folder, image_link)
            f.save(file_path)
            s.image_link = image_link

        if create_survey_form.main.data:
            main_s = Survey.query.filter_by(main=True).first()
            if main_s:
                flash("Failed to publish main survey: Main survey \"{}\" already exists.".format(s.title))
            else:
                s.main = True
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('admin.survey_view', id=s.id))
    return render_template('tools/survey/new.html', title="New Survey", form=create_survey_form)

@bp.route('/survey/<survey_id>/link/new', methods=['GET','POST'])
@login_required
def create_link(survey_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    if len(s.links) == 4:
        flash('No more than 4 links are allowed per survey.')
        return redirect(url_for('admin.survey_view', id=s.id))
    create_link_form = CreateLinkForm()
    if create_link_form.validate_on_submit():
        link = Link(
            title = create_link_form.title.data,
            description = create_link_form.description.data,
            link = create_link_form.link.data,
            survey_id = s.id
        )
        db.session.add(link)
        db.session.commit()
        # IMAGE UPLOADING LOGIC
        image_link = None
        if create_link_form.image_upload.data:
            f = create_link_form.image_upload.data
            filename = secure_filename(f.filename)
            image_link = "survey_{}_link_{}_image_{}".format(survey_id, link.id, filename)
            image_folder = os.path.abspath(os.path.dirname(__file__)) + "/../resources/images/"
            file_path = os.path.join(image_folder, image_link)
            f.save(file_path)
            link.image_link = image_link
        db.session.add(link)
        db.session.commit()
        return redirect(url_for('admin.survey_view', id=s.id))
    return render_template('tools/survey/new_link.html', title="Create a new link", form=create_link_form, survey=s)


@bp.route('/survey/<survey_id>/link/edit/<link_id>', methods=['GET','POST'])
@login_required
def edit_link(survey_id, link_id):
    s = Survey.query.filter_by(id=survey_id).first()
    l = Link.query.filter_by(id=link_id).first()
    if not s or not l:
        flash("Requested item doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    edit_link_form = EditLinkForm()
    if edit_link_form.validate_on_submit():
        l.title = edit_link_form.title.data
        l.description = edit_link_form.description.data
        l.link = edit_link_form.link.data

        # IMAGE UPLOADING LOGIC
        image_link = None
        if edit_link_form.image_upload.data:
            f = edit_link_form.image_upload.data
            filename = secure_filename(f.filename)
            image_link = "survey_{}_link_{}_image_{}".format(survey_id, l.id, filename)
            image_folder = os.path.abspath(os.path.dirname(__file__)) + "/../resources/images/"
            file_path = os.path.join(image_folder, image_link)
            f.save(file_path)
            l.image_link = image_link

        db.session.add(l)
        db.session.commit()
        return redirect(url_for('admin.survey_view', id=s.id))
    return render_template('tools/survey/edit_link.html', title="Editing link", form=edit_link_form, survey=s, link=l)

@login_required
@bp.route('/survey/<survey_id>/link/<link_id>/delete')
def delete_link(survey_id, link_id):
    l = Link.query.filter_by(id=link_id).first()
    if not l:
        flash("Requested link doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    db.session.delete(l)
    db.session.commit()
    return redirect(url_for('admin.survey_view', id=survey_id))

@bp.route('/survey/<id>')
@login_required
def survey_view(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    root = Question.query.filter_by(id=s.root_id).first()
    return render_template('tools/survey/view.html', title="Survey: {}".format(s.title), survey=s, root=root)

@bp.route('/survey/<id>/deactivate')
@login_required
def deactivate_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    if s.main:
        s.main = False
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

@bp.route('/survey/<id>/pub_main_survey')
@login_required
def pub_main_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    main_survey = Survey.query.filter_by(main=True).first()
    if main_survey:
        main_survey.main = False
    s.main = True
    s.active = True
    db.session.add(s)
    db.session.commit()
    return redirect(url_for('admin.survey_view', id=s.id))

@bp.route('/survey/<id>/depub_main_survey')
@login_required
def depub_main_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    s.main = False
    db.session.add(s)
    db.session.commit()
    return redirect(url_for('admin.survey_view', id=s.id))

@bp.route('/surveys/new/<survey_id>/question', methods=['GET', 'POST'])
@login_required
def add_question(survey_id):
    root = request.args.get('root')
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))

    add_question_form = AddQuestionForm(s.questions)
    if add_question_form.validate_on_submit():
        q = Question(
            title = add_question_form.title.data,
            description = add_question_form.description.data,
            type = add_question_form.type.data,
            survey_id = survey_id,
            default_next_id = add_question_form.default_next.data
        )
        db.session.add(q)
        db.session.commit()
        if add_question_form.root.data == True:
            s.root_id = q.id            
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('admin.question_view', survey_id=s.id, question_id=q.id))
    return render_template('tools/survey/new_question.html', title="New Question", form=add_question_form, survey=s, root=root)

@login_required
@bp.route('/survey/<survey_id>/question/<question_id>')
def question_view(survey_id, question_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    d_n = Question.query.filter_by(id=q.default_next_id).first()
    if d_n:
        q.default_next_title = d_n.title
        q.default_next_link = url_for('admin.question_view', survey_id=s.id, question_id=d_n.id)
    else:
        q.default_next_title = "Final Question (directs to summary)"
        q.default_next_link = ""
    option_data = {}
    for option in q.options:
        next_q = Question.query.filter_by(id=option.next_id).first()
        option_data[option.id] = {}
        option_data[option.id]["next_link"] = url_for("admin.question_view", survey_id=option.question.survey.id, question_id=option.next_id) if next_q else url_for("admin.question_view", survey_id=option.question.survey.id, question_id=option.question.default_next_id)
        option_data[option.id]["next_title"] = next_q.title if next_q else "No next question assigned (uses default next)"
        option_summary = Summary.query.filter_by(id=option.summary_id).first()
        option_data[option.id]["summary_link"] = url_for('admin.view_summary', survey_id=option.question.survey.id, summary_id=option_summary.id) if option_summary else ""
        option_data[option.id]["summary_title"] = option_summary.title if option_summary else "No associated summary exists"
    return render_template('tools/survey/view_question.html', title="Question: {}".format(q.title), question=q, option_data=option_data)



@bp.route('/surveys/new/<survey_id>/question/<question_id>/option', methods=['GET','POST'])
@login_required
def add_option(survey_id, question_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    # vvv THIS WHOLE SECTION CAN BE OPTIMIZED WITH ANOTHER SQL QUERY vvv
    questions = []
    for sq in s.questions:
        if sq.id != q.id: 
            questions.append(sq)
    add_option_form = AddOptionForm(questions, s.summaries)
    if add_option_form.validate_on_submit():
        o = Option(
            title = add_option_form.title.data,
            question_id = q.id
        )
        if add_option_form.next_question.data and add_option_form.next_question.data != -1:
            o.next_id = add_option_form.next_question.data
        if add_option_form.summary.data:
            o.summary_id = add_option_form.summary.data
            if add_option_form.summary_weight.data:
                o.summary_weight = add_option_form.summary_weight.data
        db.session.add(o)
        db.session.commit()
        return redirect(url_for('admin.question_view', survey_id=s.id, question_id=q.id))
    return render_template('/tools/survey/new_option.html', title="New Option", form=add_option_form, survey=s, question=q)

@bp.route('/surveys/edit/<survey_id>/question/<question_id>/delete_option/<option_id>')
@login_required
def delete_option(survey_id, question_id, option_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    o = Option.query.filter_by(id=option_id).first()
    if not o:
        flash("Requested option could not be found in database.")
        return redirect(url_for('admin.question_view', survey_id=survey_id, question_id=question_id))
    db.session.delete(o)
    db.session.commit()
    return redirect(url_for('admin.question_view', survey_id=survey_id, question_id=question_id))

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

        image_link = None
        if edit_survey_form.image_upload.data:
            f = edit_survey_form.image_upload.data
            filename = secure_filename(f.filename)
            image_link = "survey_{}_title_image_{}".format(s.id, filename)
            image_folder = os.path.abspath(os.path.dirname(__file__)) + "/../resources/images/"
            file_path = os.path.join(image_folder, image_link)
            f.save(file_path)
            s.image_link = image_link

        db.session.add(s)
        db.session.commit()
        return redirect(url_for('admin.survey_view', id=s.id))
    return render_template('tools/survey/edit.html', title="Edit Survey", form=edit_survey_form, survey=s)

@bp.route('/surveys/edit/<survey_id>/question/<question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(survey_id, question_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    edit_question_form = EditQuestionForm(Question.query.filter_by(survey_id=survey_id).filter(Question.id != question_id).all())
    if edit_question_form.validate_on_submit():
        q.title = edit_question_form.title.data
        q.description = edit_question_form.description.data
        q.type = edit_question_form.type.data
        if edit_question_form.root.data == True:
            s.root_id = q.id
        q.default_next_id = edit_question_form.default_next.data
        db.session.add(s)
        db.session.add(q)
        db.session.commit()
        back_link = request.args.get('back_link')
        return redirect(url_for('admin.survey_view', id=s.id)) if not back_link else redirect(back_link)
    edit_question_form.type.data = q.type
    edit_question_form.default_next.data = q.default_next_id
    return render_template('tools/survey/edit_question.html', title="Edit Question", form=edit_question_form, question=q, survey=s)

@bp.route('/surveys/edit/<survey_id>/delete_question/<question_id>')
@login_required
def delete_question(survey_id, question_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    db.session.delete(q)
    db.session.commit()
    return redirect(url_for('admin.survey_view', id=survey_id))

@bp.route('/surveys/edit/<survey_id>/question/<question_id>/option/<option_id>', methods=['GET', 'POST'])
@login_required
def edit_option(survey_id, question_id, option_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    q = Question.query.filter_by(id=question_id).first()
    if not q:
        flash("Requested question could not be found in database.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    o = Option.query.filter_by(id=option_id).first()
    if not o:
        flash("Requested option could not be found in database.")
        return redirect(url_for('admin.question_view', survey_id=survey_id, question_id=question_id))
    edit_option_form = EditOptionForm(Question.query.filter(Question.survey_id==survey_id).filter(Question.id != question_id).all(), s.summaries)
    if edit_option_form.validate_on_submit():
        o.title = edit_option_form.title.data
    edit_option_form.summary.data = o.summary_id 
    edit_option_form.next_question.data = o.next_id
    return render_template('/tools/survey/edit_option.html', form=edit_option_form, question=q, survey=s, option=o)

@bp.route('/surveys/<survey_id>/create_summary', methods=['GET', 'POST'])
@login_required
def create_summary(survey_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    form = CreateSummaryForm()
    if form.validate_on_submit():
        summary = Summary(
            title=form.title.data,
            description=form.description.data,
            survey_id=survey_id
        )
        db.session.add(summary)
        db.session.commit()

        image_link = None
        if form.image_upload.data:
            f = form.image_upload.data
            filename = secure_filename(f.filename)
            image_link = "survey_{}_summary_{}_image_{}".format(s.id, summary.id, filename)
            image_folder = os.path.abspath(os.path.dirname(__file__)) + "/../resources/images/"
            file_path = os.path.join(image_folder, image_link)
            f.save(file_path)
            summary.image_link = image_link
        db.session.add(summary)
        db.session.commit()

        return redirect(url_for('admin.survey_view', id=survey_id))
    return render_template('/tools/survey/new_summary.html', title="Creating Summary", form=form, survey=s)

@bp.route('/surveys/<survey_id>/view_summary/<summary_id>', methods=['GET', 'POST'])
@login_required
def view_summary(survey_id, summary_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    return render_template('/tools/survey/view_summary.html', title="Viewing summary", summary=summary, survey=survey)

@bp.route('/surveys/<survey_id>/edit_summary/<summary_id>', methods=['GET', 'POST'])
@login_required
def edit_summary(survey_id, summary_id):
    s = Survey.query.filter_by(id=survey_id).first()
    if not s:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    form = EditSummaryForm()
    if form.validate_on_submit():
        summary.title = form.title.data
        summary.description = form.description.data

        image_link = None
        if form.image_upload.data:
            f = form.image_upload.data
            filename = secure_filename(f.filename)
            image_link = "survey_{}_summary_{}_image_{}".format(s.id, summary.id, filename)
            image_folder = os.path.abspath(os.path.dirname(__file__)) + "/../resources/images/"
            file_path = os.path.join(image_folder, image_link)
            f.save(file_path)
            summary.image_link = image_link

        db.session.add(summary)
        db.session.commit()
        return redirect(url_for('admin.survey_view', id=survey_id))    
    return render_template('/tools/survey/edit_summary.html', survey=s, summary=summary, form=form)

@bp.route('/surveys/<survey_id>/delete_summary/<summary_id>', methods=['GET', 'POST'])
@login_required
def delete_summary(survey_id, summary_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    db.session.delete(summary)
    db.session.commit()
    return redirect(url_for('admin.survey_view', id=survey_id))

@bp.route('/surveys/<survey_id>/summary/<summary_id>/new_info_group', methods=['GET', 'POST'])
@login_required
def create_info_group(survey_id, summary_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
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
        return redirect(url_for('admin.view_summary', survey_id=survey_id, summary_id=summary_id))
    
    return render_template('/tools/survey/new_info_group.html', 
                            title="Create Summary Information Group", 
                            form=form, 
                            survey=survey, 
                            summary=summary
                          )


@bp.route('/surveys/<survey_id>/summary/<summary_id>/info_group/<infogroup_id>/delete')
@login_required
def delete_info_group(survey_id, summary_id, infogroup_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        flash("Requested survey doesn't exist.")
        return redirect(url_for('admin.survey_home'))
    summary = Summary.query.filter_by(id=summary_id).first()
    if not summary:
        flash("Requested summary doesn't exist.")
        return redirect(url_for('admin.survey_view', id=survey_id))
    infogroup = SummaryInfoGroup.query.filter_by(id=infogroup_id).first()
    if not infogroup:
        flash("Requested info group doesn't exist.")
        return redirect(url_for('admin.view_summary', survey_id=survey.id, summary_id=summary.id))
    db.session.delete(infogroup)
    db.session.commit()
    return redirect(url_for('admin.view_summary', survey_id=survey.id, summary_id=summary.id))

@bp.route('/surveys/survey_design_guide/<survey_id>/<survey_title>')
@login_required
def survey_design_guide(survey_id, survey_title):
    return render_template('/tools/survey/survey_design_guide.html', title="Survey Design Guide", survey_id=survey_id, survey_title=survey_title)

#---------------------------------------------------------------------------------------------#
#    DEVELOPMENT ADMINISTRATION ROUTES: get status of git repos and deployments               #
#---------------------------------------------------------------------------------------------#

@bp.route('/development')
@login_required
def development_home():
    return render_template('tools/dev/home.html', title="Dev Dashboard")