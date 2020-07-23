from flask_restplus import Resource
# Import all service functions
from ..service.illness_service import (
    get_illness,
    check_symptoms,
    get_active_illness,
    get_illness_history,
    save_symptoms,
    close_active_illness,
    export_active_illness_report,
    edit_illness_title,
    get_symptoms_list
)
from ..util.dto import IllnessDTO
from flask import request
from ..util.decorator import token_required

api = IllnessDTO.api
_get_by_id = IllnessDTO.get_by_id
_check_symptoms = IllnessDTO.check_symptoms
_save_symptoms = IllnessDTO.save_symptoms
_edit_illness_title = IllnessDTO.edit_illness_title


@api.route('/get_illness_by_id')
class GetIllness(Resource):
    @api.doc(responses={
        200: 'Successfully retrieved illness',
        401: 'Failed to authenticate.'
    })
    @api.doc('get illness information by its id')
    @api.expect(_get_by_id, validate=True)
    @token_required
    def post(self, auth_object):
        """Get Illness by ID"""
        data = request.json
        user_id = auth_object['auth_object']['data']['user_id']
        return get_illness(data['id'], user_id)


@api.route('/edit_illness_title')
class EditIllnessTitle(Resource):
    @api.doc(responses={
        200: 'Successfully edited illness title',
        401: 'Failed to authenticate.',
        404: 'Failed to retrieve illness with given id'
    })
    @api.expect(_edit_illness_title, validate=True)
    @token_required
    def post(self, auth_object):
        """Edit Illness Title"""
        data = request.json
        illness_id = data['illness_id']
        new_title = data['new_title']
        user_id = auth_object['auth_object']['data']['user_id']
        return edit_illness_title(user_id, illness_id, new_title)


@api.route('/check_symptoms')
class CheckSymptoms(Resource):
    @api.doc(responses={
        200: 'Successfully submitted symptom string',
        401: 'Failed to authenticate'
    })
    @api.expect(_check_symptoms)
    @token_required
    def post(self, auth_object):
        """Check symptom string"""
        data = request.json
        return check_symptoms(data)


@api.route('/save_symptoms')
class SaveSymptoms(Resource):
    @api.doc(responses={
        200: 'Successfully saved symptoms to active illness',
        401: 'Failed to authenticate'
    })
    @api.expect(_save_symptoms)
    @token_required
    def post(self, auth_object):
        """Save symptom string"""
        data = request.json
        user_id = auth_object['auth_object']['data']['user_id']
        return save_symptoms(data, user_id)


@api.route('/close_active_illness')
class CloseActiveIllness(Resource):
    @api.doc(responses={
        200: 'Successfully ended active illness',
        401: 'Failed to authenticate'
    })
    @token_required
    def get(self, auth_object):
        """Close current active illness"""
        user_id = auth_object['auth_object']['data']['user_id']
        return close_active_illness(user_id)


@api.route('/get_active_illness')
class GetActiveIllness(Resource):
    @api.doc(responses={
        200: 'Successfully retrieved user\'s active illness',
        401: 'Failed to authenticate'
    })
    @api.doc('endpoint for retrieving a user\'s active illness')
    @token_required
    def get(self, auth_object):
        """Get user's illness"""
        user_id = auth_object['auth_object']['data']['user_id']
        return get_active_illness(user_id)


@api.route('/get_illness_history')
class GetIllnessHistory(Resource):
    @api.doc(responses={
        200: 'Successfully retrieved user\'s illness history',
        401: 'Failed to authenticate'
    })
    @api.doc('endpoint for retrieving a user\'s illness history')
    @token_required
    def get(self, auth_object):
        """Get user's illness history"""
        user_id = auth_object['auth_object']['data']['user_id']
        return get_illness_history(user_id)


@api.route('/export_active_illness/illness.pdf')
class ExportActiveIllness(Resource):
    @api.doc(responses={
        200: 'Successfully generated report and returned to user'
    })
    @api.doc('endpoint for generating PDF for report and returning to user')
    @token_required
    def get(self, auth_object):
        """Get report for user's active illness"""
        user_id = auth_object['auth_object']['data']['user_id']
        return export_active_illness_report(user_id)


@api.route('/get_symptoms_list')
class GetSymptomsList(Resource):
    @api.doc(responses={
        200: 'Successfully retrieved symptoms list'
    })
    @api.doc('endpoint for retrieving list of existing symptoms')
    def get(self):
        """Return list of infermedica symptoms"""
        return get_symptoms_list()
