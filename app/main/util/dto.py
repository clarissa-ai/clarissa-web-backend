from flask_restplus import Namespace, fields

class UserDTO:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'email': fields.String(required=True, description='user email address'),
        'first_name': fields.String(required=True, description='user first name'),
        'password': fields.String(description='user password'),
    })

class AuthDTO:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
    })

class SurveyDTO:
    api = Namespace('survey', description='survey related operations')
    survey = api.model('survey_details', {

    })
    get_survey = api.model('get_survey_endpoint', {
        'id': fields.Integer(required=True, description='The id of the survey')
    })