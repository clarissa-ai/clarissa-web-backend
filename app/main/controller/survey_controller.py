from flask import request
from flask_restplus import Resource

from ..util.dto import SurveyDTO
from ..service.survey_service import (
    get_active_surveys,
    get_survey,
    get_main_survey,
    post_survey_response,
    get_survey_results
)


api = SurveyDTO.api
_get_survey = SurveyDTO.get_survey
_post_survey_response = SurveyDTO.post_survey_response


@api.route('/get_active_surveys')
class ActiveSurveys(Resource):
    @api.doc('get a list of all active surveys')
    @api.response(200, 'Active surveys retrieved')
    def get(self):
        """Get list of all active surveys"""
        return get_active_surveys()


@api.route('/get_survey_by_id')
class Survey(Resource):
    @api.doc('get a survey by an id')
    @api.response(200, 'Survey data retrieved')
    @api.expect(_get_survey, validate=True)
    def post(self):
        """Get a survey by id"""
        data = request.json
        return get_survey(data['id'])


@api.route('/get_main_survey')
class MainSurvey(Resource):
    @api.doc('get information about the main survey')
    @api.response(200, 'Main survey retrieved')
    def get(self):
        """Get info about the main published survey"""
        return get_main_survey()


@api.route('/submit_response')
class SubmitResponse(Resource):
    @api.doc('submit a response to a survey')
    @api.doc(responses={
        400: 'Failed to submit survey',
        200: 'Response successfully submitted.'
    })
    @api.expect(_post_survey_response, validate=True)
    def post(self):
        """Submit survey response JSON"""
        data = request.json
        return post_survey_response(data)

@api.route('/get_response')
class GetResponse(Resource):
    @api.doc('get a list of all submitted surveys by user')
    @api.response(200, 'Submitted surveys results retrieved')
    def get(self):
        """Get list of all submitted survey results"""
        return get_survey_results()