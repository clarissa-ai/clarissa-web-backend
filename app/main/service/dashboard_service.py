from app.main.model.user import User
from app.main.model.survey import Response, Survey
from app.main.model.illness import Illness
from app.main import db
import datetime


def get_dashboard(auth_object):
    user_id = auth_object['auth_object']['data']['user_id']
    user = User.query.filter_by(id=user_id).first()
    active_illness = Illness.query.filter_by(
        user_id=user_id,
        active=True
    ).first() != None  # noqa: E711
    active_surveys = Survey.get_active_surveys()
    if len(active_surveys) > 2:
        active_surveys = active_surveys[0:2]
    response_object = {
        'active_illness': active_illness,
        'symptom_count': len(user.symptoms),
        'illness_count': len(user.illnesses),
        'response_count': Response.query.filter_by(user_id=user_id).count(),
        'active_surveys': [{
            'id': s.id,
            'title': s.title,
        } for s in active_surveys],
    }
    response_object['completed_surveys'] = []
    completed_counter = 0
    for s in Survey.query.order_by(-Survey.id).all():
        if Response.query.filter_by(user_id=user_id, survey_id=s.id).first():
            if completed_counter < 2:
                response_object['completed_surveys'].append({
                    'id': s.id,
                    'title': s.title
                })
            completed_counter = completed_counter + 1
    response_object['recent_illnesses'] = [
        {
            'id': i.id,
            'active': i.active,
            'created_on': i.created_on.strftime("%m/%d/%Y %I:%M:%S%p"),
            'updated_on': i.updated_on.strftime("%m/%d/%Y %I:%M:%S%p"),
            'symptom_count': len(i.symptoms)
        } for i in Illness.query.filter_by(
            user_id=user_id
        ).order_by(-Illness.id).limit(5)
    ]
    return response_object, 200


def create_illness(user_id):
    response_object = {
        'status': 'success'
    }
    user = User.query.filter_by(id=user_id).first()
    recent_illness = Illness.query.filter_by(
        user_id=user.id
    ).order_by(-Illness.id).first()
    if recent_illness and recent_illness.active:
        recent_illness.active = False
        db.session.add(recent_illness)
        db.session.commit()
        response_object['message'] = (
            'Deactivated current active illness and'
            'created new illness'
        )
    else:
        response_object['message'] = 'Created new illness'
    new_illness = Illness(
        user_id=user.id,
        active=True,
        created_on=datetime.datetime.utcnow()
    )
    db.session.add(new_illness)
    db.session.commit()
    return response_object, 200
