from flask import request
from flask_restplus import Resource

from ..util.dto import UserDTO
from ..service.user_service import save_new_user, get_all_users
from ..service.auth_helper import Auth
from ..util.decorator import token_required

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


@token_required
@api.route('/get_user_info')
class GetUserInfo(Resource):
    @api.response(200, "User data retrieved")
    @api.doc('get info about user from token')
    def get(self):
        """All user info for authenticated user"""
        return Auth.get_logged_in_user(request)
