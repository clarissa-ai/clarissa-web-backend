import datetime

from app.main import db
from app.main.model.survey import Survey, Question, Option

def save_model(data):
    db.session.add(data)
    db.session.commit(data)

def get_main_survey():
    s = Survey.get_main_survey()
    response_object = {}
    if not s:
        response_object = {
            'status': 'failure',
            'message': 'Failed to retreive main survey, main survey not published.'
        }
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved main published survey.',
        'survey': {
            'id': s.id,
            'title': s.title
        }
    }
    return response_object

def get_active_surveys():
    surveys = []
    for s in Survey.query.all():
        if s.expiration_date < datetime.datetime.utcnow() and s.active == True:
            s.active == False
            save_model(s)
        elif s.active == True:
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

