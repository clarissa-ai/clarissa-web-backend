from flask_restplus import Namespace, fields


class UserDTO:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'email': fields.String(
            required=True,
            description='user email address',
            example='korra@dogmail.com',
            pattern=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        ),
        'first_name': fields.String(
            required=True,
            description='user first name',
            example='Korra'
        ),
        'password': fields.String(
            required=True,
            description='user password',
            example='Bark2020'
        ),
    })


class AuthDTO:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(
            required=True,
            description='The email address',
            example='korra@dogmail.com'
        ),
        'password': fields.String(
            required=True,
            description='The user password',
            example='Bark2020'
        ),
    })


class SurveyDTO:
    api = Namespace('survey', description='survey related operations')
    get_survey = api.model('get_survey_endpoint', {
        'id': fields.Integer(
            required=True,
            description='The id of the survey',
            example=1
        )
    })

    post_survey_response = api.model('post_survey_response', {
        'survey_id': fields.Integer(
            required=True,
            description='ID of the survey for which a response is submitted',
            example=1
        ),
        'user_email': fields.String(
            description='Email of the user submitting the report (Optional)',
            example='korra@dogmail.com'
        ),
        'json_body': fields.Raw(
            required=True,
            example={
                '1': ['coughing', 'vomiting']
            }
        )
    })


class ImageDTO:
    api = Namespace('image', description='image retrieval operations')


class RouteDTO:
    api = Namespace('route', description='custom route retrieval')
