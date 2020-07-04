import datetime
from flask import request

from app.main import db
from app.main.model.survey import Survey, Response, Question, Summary
from app.main.model.user import User
from app.main.service.auth_helper import Auth

from sqlalchemy import exc as exceptions


def save_model(data):
    db.session.add(data)
    db.session.commit()


def get_main_survey():
    s = Survey.get_main_survey()
    response_object = {}
    if not s:
        response_object = {
            'status': 'failure',
            'message': 'Failed to retreive main survey, \
                main survey not published.'
        }
    else:
        response_object = {
            'status': 'success',
            'message': 'Successfully retrieved main published survey.',
            'survey': {
                'id': s.id,
                'title': s.title,
                'description': s.description,
                'cover_image_url': s.get_cover_image_url(),
                'question_count': len(s.questions)
            }
        }
        auth_response, auth_response_code = Auth.get_logged_in_user(request)
        if auth_response_code == 200:
            user = auth_response.get('data')
            response_object['survey']['completed'] = Response.query.filter_by(
                survey_id=s.id,
                user_id=user.get('user_id')
            ).first() != None  # noqa: E711
    return response_object, 200


def get_active_surveys():
    surveys = []
    for s in Survey.query.all():
        if s.expiration_date < datetime.datetime.utcnow() and s.active:
            s.active = False
            save_model(s)
        elif s.active:
            surveys.append({
                'id': s.id,
                'title': s.title,
                'description': s.description,
                'cover_image_url': s.get_cover_image_url(),
                'question_count': len(s.questions)
            })
            auth_response, auth_response_code = Auth.get_logged_in_user(
                request
            )
            if auth_response_code == 200:
                user = auth_response.get('data')
                surveys[-1]['completed'] = Response.query.filter_by(
                    survey_id=s.id,
                    user_id=user.get('user_id')
                ).first() != None  # noqa: E711
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved surveys.',
        'surveys': surveys
    }
    return response_object, 200


def get_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if not s:
        response_object = {
            'status': 'failure',
            'message': 'Failed to retrieve survey with id: {}'.format(id)
        }
        return response_object, 200
    else:
        response_object = {
            'status': 'success',
            'message': 'Successfully retrieved survey.',
            'survey': s.get_json()
        }
        return response_object, 200


def post_survey_response(data):
    s = Survey.query.filter_by(id=data['survey_id']).first()
    if not s:
        return {
            'status': 'failure',
            'message': 'Failed to retrieve survey with id: {}'.format(
                data['survey_id']
            )
        }, 400
    u = None
    if 'user_email' in data.keys():
        u = User.query.filter_by(email=data['user_email']).first()
        if not u:
            return {
                'status': 'failure',
                'message': 'Failed to retrieve user with email: {}'.format(
                    data['user_email']
                )
            }, 400
    r = Response(
        survey_id=s.id,
        json_response=data['json_body']
    )
    if u:
        r.user_id = u.id
    try:
        db.session.add(r)
        db.session.commit()
    except exceptions.SQLAlchemyError:
        return {
            'status': 'failure',
            'message': 'Failed to add response to database.'
        }, 500
    return {
        'status': 'success',
        'message': 'Successfully submitted survey response.'
    }, 200


def get_survey_results():
    surveys_answers = []
    auth_response, auth_response_code = Auth.get_logged_in_user(request)

    if auth_response_code == 200:
        user = auth_response.get('data')
        for s in Survey.query.all():
            response_json = Response.query.filter_by(survey_id=s.id, user_id=user.get('user_id')).order_by(-Response.id).first()
            if response_json:
                json_body = response_json.json_response
                questions = json_body['questions']
                question_responses = []
                for q in questions:
                    if q['choices'] != []:
                        question_responses.append({
                            'title': Question.query.filter_by(id=q['id']).first().title,
                            'choices': q['choices']
                        })
                summary = Summary.query.filter_by(id=json_body['summary']['id']).first()
                surveys_answers.append({
                    'title': s.title,
                    'description': s.description,
                    'cover_image_url': s.get_cover_image_url(),
                    'answered_questions': question_responses,
                    'summary_title': summary.title,
                    'summary_description': summary.description
                })
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved surveys results.',
        'surveys': surveys_answers
    }
    return response_object, 200
