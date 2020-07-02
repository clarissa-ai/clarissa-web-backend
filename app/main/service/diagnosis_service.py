# import User model and change function params according
# to User model storage
import requests
import os
from dotenv import load_dotenv
load_dotenv()


def post_user_response_to_api(user_json, user_sex, user_age):
    """Function to query API for user symptoms and diagnosis based on user age
       and user sex

    Args:
        user_json (JSON): User response to how they are feeling.
        user_sex (string): gender/sex of user
        user_age (int): age of user

    Returns:
        symptoms: JSON of all symptoms details
        diagnosis: JSON of possible conditions + follow-up questions
    """
    # use user_id to get user's sex, age and store that in variables
    # user_sex and user_age, input that into diagnosis endpoint
    data = dict([('sex', user_sex), ('age', user_age)])
    data_syms = []
    headers = {
      'App-Id': os.getenv('API_APP_ID'),
      'App-Key': os.getenv('API_APP_KEY'),
      'Content-Type': 'application/json'
    }
    url1 = "https://api.infermedica.com/v2/parse"
    symptoms = requests.post(url1, headers=headers, json=user_json).json()
    for i in range(0, len(symptoms['mentions'])):
        data_syms.append({'id': symptoms['mentions'][i]['id'],'choice_id': 'present'})
    data.update([('evidence', data_syms)])
    url2 = "https://api.infermedica.com/v2/diagnosis"
    print(data)
    diagnosis = requests.post(url2, headers=headers, json=data).json()
    return symptoms, diagnosis
