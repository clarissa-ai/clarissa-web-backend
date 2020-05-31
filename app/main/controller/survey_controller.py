from flask import request
from flask_restplus import Resource

from ..util.dto import SurveyDTO
from..service.survey_service import save_model, get_active_surveys, get_survey

from ..util.decorator import token_required, admin_token_required

api = SurveyDTO.api
_get_survey = SurveyDTO.get_survey

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