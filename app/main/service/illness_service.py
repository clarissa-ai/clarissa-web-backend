from app.main.model.illness import Illness, Symptom, Diagnosis
from app.main.model.user import User
import requests
import os
import datetime
from app.main import db


def get_illness(id, user_id):
    response_object = {}
    try:
        illness = Illness.query.filter_by(id=id).first()
    except Exception as e:
        print(e)
        return {
            'status': 'failure',
            'message': 'Failed to fetch'
        }, 400
    if not illness or user_id != illness.user_id:
        response_object = {
            'status': 'failure',
            'message': 'Failed to retrieve illness with given id.'
        }
        return response_object, 404
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved illness.',
        'illness': illness.get_json()
    }
    return response_object, 200


def check_symptoms(data):
    response_object = {}
    headers = {
      'App-Id': os.getenv('API_APP_ID'),
      'App-Key': os.getenv('API_APP_KEY'),
      'Content-Type': 'application/json'
    }
    NLP_URL = "https://api.infermedica.com/v2/parse"
    symptoms = requests.post(NLP_URL, headers=headers, json=data).json()
    response_object = {
        'status': 'success',
        'message': 'Successfully processed user symptom request',
        'symptoms_json': symptoms
    }
    return response_object, 200


def get_active_illness(user_id):
    active_illness = Illness.query.filter_by(
        user_id=user_id,
        active=True
    ).first()
    if not active_illness:
        return {
            'status': 'success',
            'message': 'Successfully retrieved active illness',
            'illness': {}
        }, 200
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved active illness',
        'illness': Illness.query.filter_by(
            user_id=user_id,
            active=True
        ).first().get_json()
    }
    response_object['illness']['analysis'] = response_object['illness'].pop(
        'diagnosis'
    )
    return response_object, 200


def close_active_illness(user_id):
    response_object = {
        'status': 'success'
    }
    active_illness = Illness.query.filter_by(
        user_id=user_id
    ).order_by(-Illness.id).first()
    if active_illness.active:
        response_object['message'] = 'Successfully deactivated active illness'
        active_illness.active = False
    else:
        response_object['message'] = 'No active illness found'
    db.session.add(active_illness)
    db.session.commit()
    return response_object, 200


def calculate_age(born):
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))  # noqa: E501


def save_symptoms(data, user_id):
    user = User.query.filter_by(id=user_id).first()
    response_object = {
        'status': 'success'
    }
    active_illness = Illness.query.filter_by(
        user_id=user_id,
        active=True
    ).first()
    if not active_illness:
        response_object['message'] = (
            'Active illness not found, created new active illness'
            'and added symptoms'
        )
        active_illness = Illness(
            user_id=user_id,
            active=True,
            created_on=datetime.datetime.utcnow()
        )
        db.session.add(active_illness)
        db.session.commit()
    else:
        response_object['message'] = (
            'Added symptoms to active illness.'
        )
    for s in data['symptoms']:
        new_symptom = Symptom(
            user_id=user_id,
            illness_id=active_illness.id,
            title=s['common_name'],
            data=s
        )
        db.session.add(new_symptom)
        db.session.commit()
    active_illness.updated_on = datetime.datetime.now()
    db.session.add(active_illness)
    db.session.commit()
    # Symptoms are saved to illness, starting diagnosis
    headers = {
      'App-Id': os.getenv('API_APP_ID'),
      'App-Key': os.getenv('API_APP_KEY'),
      'Content-Type': 'application/json'
    }
    diagnosis_url = "https://api.infermedica.com/v2/diagnosis"
    diagnosis_json = {
        'evidence': [],
    }
    diagnosis_json['sex'] = user.sex.lower() if user.sex != "None" else 'male'
    diagnosis_json['age'] = calculate_age(user.birthdate)
    for s in Symptom.query.filter_by(
        user_id=user_id,
        illness_id=active_illness.id
    ).order_by(-Symptom.id).all():
        diagnosis_json['evidence'].append({
            'id': s.data['id'],
            'choice_id': 'present'
        })
    diagnosis = requests.post(
        diagnosis_url,
        headers=headers,
        json=diagnosis_json
    ).json()
    # add explanations for each condition
    conditions = diagnosis['conditions']
    explanation_URL = "https://api.infermedica.com/v2/explain"
    for idx, c in enumerate(conditions):
        c_json = {
            'sex': user.sex.lower() if user.sex != "None" else 'male',
            'age': calculate_age(user.birthdate),
            'target': c['id'],
            'evidence': [{
                'id': s.data['id'],
                'choice_id': 'present'
            } for s in active_illness.symptoms]
        }
        explanation = requests.post(
            explanation_URL,
            headers=headers,
            json=c_json
        ).json()
        c['supporting_symptoms'] = explanation.get('supporting_evidence') or []
        c['opposing_symptoms'] = (explanation.get('conflicting_evidence') or []) + (explanation.get('unconfirmed_evidence') or [])  # noqa: E501
        # update active_diagnosis with data for condition
        conditions[idx] = c
    # save diagnosis to db
    d = Diagnosis(
        user_id=user_id,
        illness_id=active_illness.id,
        data=conditions
    )
    db.session.add(d)
    db.session.commit()
    return response_object, 200


def get_illness_history(user_id):
    illnesses = []
    for i in Illness.query.filter_by(
        user_id=user_id,
        active=False
    ).order_by(-Illness.id).all():
        illnesses.append(i.get_json())
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved user\'s illness history',
        'illnesses': illnesses
    }
    return response_object, 200
