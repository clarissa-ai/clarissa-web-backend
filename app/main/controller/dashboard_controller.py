from flask_restplus import Resource
# Import all service functions
from ..service.dashboard_service import (
    get_dashboard,
    create_illness
)
from ..util.dto import DashboardDTO
from ..util.decorator import token_required

api = DashboardDTO.api


@api.route('/get_dashboard')
class GetDashboard(Resource):
    @api.doc(responses={
        200: 'Successfully retrieved dashboard data',
        401: 'Failed to authenticate'
    })
    @api.doc('get dashboard data')
    @token_required
    def get(self, auth_object):
        """Retrieved user's dashboard data"""
        return get_dashboard(auth_object)


@api.route('/create_illness')
class CreateActiveIllness(Resource):
    @api.doc(responses={
        200: 'Successfully created a new active illness',
        401: 'Failed to authenticate'
    })
    @token_required
    def get(self, auth_object):
        """Create an active illness"""
        user_id = auth_object['auth_object']['data']['user_id']
        return create_illness(user_id)
