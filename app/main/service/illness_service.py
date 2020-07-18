# python library imports
import requests
import os
import datetime
import json
# Database imports
from app.main.model.illness import Illness, Symptom, Diagnosis
from app.main.model.user import User
from app.main import db
# Utility imports
from flask_weasyprint import HTML, render_pdf
from flask import render_template


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


def edit_illness_title(user_id, illness_id, new_title):
    illness = Illness.query.filter_by(user_id=user_id, id=illness_id).first()
    if not illness:
        return {
            'status': 'failure',
            'message': 'Failed to modify illness with given id.'
        }, 404
    illness.title = new_title
    try:
        db.session.add(illness)
        db.session.commit()
        return {
            'status': 'success',
            'message': 'Successfully modified illness title.'
        }
    except Exception as e:
        print(e)
        return {
            'status': 'failure',
            'message': 'An error has occurred during this request.'
        }, 400


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
        active_illness.updated_on = datetime.datetime.now()
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

    # function to generate condition url based on id from diagnosis
    def condition_URL(condition_id):
        return "https://api.infermedica.com/v2/conditions/{}".format(
            condition_id
        )
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
        # THE CONDITIONS ENDPOINT IS UNNECESSARY AND CAN BE CACHED LOCALLY
        condition_info = requests.get(
            condition_URL(c['id']),
            headers=headers
        ).json()
        c['hint'] = condition_info.get('extras').get('hint')
        c['categories'] = condition_info.get('categories')
        c['prevalence'] = condition_info.get('prevalence')
        c['severity'] = condition_info.get('severity')
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


def export_active_illness_report(user_id):
    # retrieve user's active illness
    active_illness = Illness.query.filter_by(
        user_id=user_id,
        active=True
    ).first()
    # generate html from template and illness data
    report_html = render_template(
        '/api/illness/illness_report.html',
        illness=active_illness
    )
    return render_pdf(HTML(string=report_html))


# Retrieving and loading symptoms list
CURR_PATH = os.path.dirname(os.path.realpath(__file__))
SYMPTOMS_FILE_PATH = os.path.join(
    CURR_PATH,
    './resources/infermedica_symptoms_list.json'
)
LOADED_SYMPTOMS = None
if os.path.isfile(SYMPTOMS_FILE_PATH):
    with open(SYMPTOMS_FILE_PATH, 'r') as symptoms_json:
        LOADED_SYMPTOMS = json.load(symptoms_json)


def get_symptoms_list():
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved symptoms list',
        'symptoms': LOADED_SYMPTOMS
    }
    return response_object, 200


def download_symptoms_json():
    headers = {
      'App-Id': os.getenv('API_APP_ID'),
      'App-Key': os.getenv('API_APP_KEY'),
      'Content-Type': 'application/json'
    }
    symptoms_url = "https://api.infermedica.com/v2/symptoms"
    symptoms_resp = requests.get(
        symptoms_url,
        headers=headers
    )
    symptoms = symptoms_resp.json()
    with open(SYMPTOMS_FILE_PATH, 'w+') as output_f:
        json.dump(symptoms, output_f)
    print('Successfully loaded symptoms list from Infermedica API')


# Will run whenever the file is loaded (on application start)
download_symptoms_json()
