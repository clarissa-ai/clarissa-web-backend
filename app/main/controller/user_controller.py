import os
from flask import request, after_this_request
from flask_restplus import Resource

from ..util.dto import UserDTO
from ..service.user_service import (
    save_new_user,
    get_all_users,
    set_cookie,
    edit_user_settings
)
from ..service.auth_helper import Auth
from ..util.decorator import token_required

api = UserDTO.api
_user = UserDTO.user
_settings = UserDTO.settings

# Only allow this route in development
if not os.environ.get('DEPLOY_ENV') == 'PRODUCTION':
    @api.route('/users')
    class UserList(Resource):
        @token_required
        @api.doc('List of registered users, only available in development')
        @api.marshal_list_with(_user, envelope='data')
        def get(self, auth_object):
            """List all registered users"""
            return get_all_users(auth_object)


@api.route('/register')
class Registration(Resource):
    @api.doc(responses={
        201: 'User successfully registered.',
        400: 'Failed to validate payload.',
        409: 'User already exists.'
    })
    @api.doc('create a new user')
    @api.expect(_user, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json

        @after_this_request
        def jwt_cookie_setter(response):
            return set_cookie(response, data)
        return save_new_user(data=data)


@api.route('/get_user_info')
class GetUserInfo(Resource):
    @api.doc(responses={
        200: 'User information retrieved.',
        401: 'Failed to validate user token'
    })
    @api.doc('get info about user from token')
    def get(self):
        """All user info for authenticated user"""
        return Auth.get_logged_in_user(request)


@api.route('/edit_settings')
class GetEditSettings(Resource):
    @api.doc(responses={
        200: 'Successfully edited user settings',
        404: 'Failed to find user by id'
    })
    @api.doc('edit a logged in user\'s settings')
    @token_required
    @api.expect(_settings, validate=True)
    def post(self, auth_object):
        """Submit new user settings"""
        return edit_user_settings(request.json, auth_object)
