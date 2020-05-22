from flask import request
from flask_restplus import Resource

from ..util.dto import UserDTO
from..service.user_service import save_new_user, get_all_users, get_user_by_id

api = UserDTO.api
_user = UserDTO.user

@api.route('/users')
class UserList(Resource):
    @api.doc('list_of_registered_users')
    @api.marshal_list_with(_user, envelope='data')
    def get(self):
        """List all registered users"""
        return get_all_users()

@api.route('/register')
class Registration(Resource):
    @api.response(201, 'User successfully registered.')
    @api.doc('create a new user')
    @api.expect(_user, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)