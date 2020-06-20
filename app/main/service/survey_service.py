import datetime

from app.main import db
from app.main.model.survey import Survey, Response
from app.main.model.user import User

from sqlalchemy import exc as exceptions



def save_model(data):
    db.session.add(data)
    db.session.commit(data)


def get_main_survey():
    s = Survey.get_main_survey()
    response_object = {}
    if not s:
        response_object = {
            'status': 'failure',
            'message': 'Failed to retreive main survey, \
                main survey not published.'
        }
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved main published survey.',
        'survey': {
            'id': s.id,
            'title': s.title
        }
    }
    return response_object, 200


def get_active_surveys():
    surveys = []
    for s in Survey.query.all():
        if s.expiration_date < datetime.datetime.utcnow() and s.active:
            save_model(s)
        elif s.active:
            surveys.append({
                'id': str(s.id),
                'title': s.title
            })
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
    if data['user_email']:
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
