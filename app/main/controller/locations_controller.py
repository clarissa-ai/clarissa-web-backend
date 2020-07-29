from flask_restplus import Resource
from ..service.location_service import (
    get_nyu_locations,
    get_location_history,
    add_location
)
from ..util.dto import LocationDTO
from ..util.decorator import token_required
from flask import request

api = LocationDTO.api
_add_location = LocationDTO.add_location


@api.route('/get_nyu_locations')
class GetNYULocations(Resource):
    @api.doc(responses={
        200: 'Successfully retrieved NYU locations list.'
    })
    @api.doc('Get NYU locations')
    def get(self):
        """Gets NYU locations json"""
        return get_nyu_locations()


@api.route('/get_location_history')
class GetLocationHistory(Resource):
    @api.doc(responses={
        200: 'Successfully retrieved user location history',
        401: 'Failed to authenticate'
    })
    @token_required
    def get(self, auth_object):
        """Get user's location history"""
        user_id = auth_object['auth_object']['data']['user_id']
        return get_location_history(user_id)


@api.route('/add_location')
class AddLocation(Resource):
    @api.doc(responses={
        200: 'Successfully added location to user history'
    })
    @api.expect(_add_location)
    @token_required
    def post(self, auth_object):
        """Add location to user location history"""
        data = request.json
        user_id = auth_object['auth_object']['data']['user_id']
        date = None
        if data.get('date_visited'):
            date = data['date_visited']
        return add_location(user_id, data['name'], date)
