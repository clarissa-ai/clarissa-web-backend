from flask_restplus import Resource


from ..util.dto import RouteDTO
from ..service.routes_service import get_routes

api = RouteDTO.api


@api.route('/routes')
class RoutesList(Resource):
    @api.doc('list_of_custom_routes')
    def get(self):
        """List all custom routes"""
        return get_routes()
