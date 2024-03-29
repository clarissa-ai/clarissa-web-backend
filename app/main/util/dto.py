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
        'birthdate': fields.String(
            required=True,
            description='user date of birth',
            example='08/26/1992',
            pattern=r"^\d{2}/\d{2}/\d{4}$"
        ),
        'password': fields.String(
            required=True,
            description='user password',
            example='Bark2020'
        ),
        'sex': fields.String(
            required=True,
            description='user sex',
            example='Male'
        ),
    })
    settings = api.model('user_settings', {
        'current_password': fields.String(
            description='user\'s current password',
            example='Bark2020'
        ),
        'password': fields.String(
            description='user\'s new password',
            example='Bark2020'
        ),
        'email': fields.String(
            description='user email address',
            example='korra@dogmail.com',
            pattern=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        ),
        'first_name': fields.String(
            description='user first name',
            example='Korra'
        ),
        'birthdate': fields.String(
            description='user date of birth - UTC JavaScript Date format',
            example='2000-02-26T05:00:00.000Z',
            pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$"
        ),
        'sex': fields.String(
            description='user\'s current sex',
            example='Female'
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


class IllnessDTO:
    api = Namespace('illness', description='illness operations')
    get_by_id = api.model('get_illness_by_id', {
        'id': fields.Integer(
            required=True,
            description='ID of the illness which is being retrieved',
            example=1
        )
    })
    check_symptoms = api.model('check_symptoms', {
        'text': fields.String(
            required=True,
            description='The string to by process by NLP entered by the user',
            example='I have a mild stomach ache'
        )
    })
    save_symptoms = api.model('save_symptoms', {
        'symptoms': fields.Raw(
            required=True,
            description='Symptoms selected by the user to save to the illness',
            example=[{
                "id": "s_1782",
                "name": "Abdominal pain, mild",
                "common_name": "Mild stomach pain",
                "orth": "mild stomach ache",
                "choice_id": "present",
                "type": "symptom"
            }]
        )
    })
    edit_illness = api.model('edit_illness', {
        'illness_id': fields.Integer(
            required=True,
            description='ID of the illness being changed by the user',
            example=1
        ),
        'new_title': fields.String(
            required=True,
            description='New title of the illness',
            example='Post-Thanksgiving Flu'
        ),
        'start_date': fields.String(
            required=False,
            description='The date the illness started',
            example='2017-02-26T05:00:00.000Z',
            pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$"
        ),
        'end_date': fields.String(
            required=False,
            description='The date the illness ended',
            example='2017-02-26T05:00:00.000Z',
            pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$"
        )
    })
    reopen_illness = api.model('reopen_illness', {
        'illness_id': fields.Integer(
            required=True,
            description='the id of the illness to be reopened',
            example=1
        )
    })
    edit_symptoms = api.model('edit_symptoms', {
        'symptom_id': fields.Integer(
            required=True,
            description='ID of the illness being changed by the user',
            example=1
        ),
        'new_date': fields.String(
            description='start date of symptom - UTC JavaScript Date format',
            example='2000-02-26T05:00:00.000Z',
            pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$"
            # ex: 2000-02-26T05:00:00.000Z
        ),
    })
    delete_symptoms = api.model('delete_symptoms', {
        'symptom_id': fields.Integer(
            required=True,
            description='ID of the illness being deleted by the user',
            example=1
        ),
    })


class DashboardDTO:
    api = Namespace('dashboard', description='dashboard operations')
