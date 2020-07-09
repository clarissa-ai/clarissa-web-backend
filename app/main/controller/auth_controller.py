from flask import request, after_this_request
from flask_restplus import Resource

from app.main.service.auth_helper import Auth
from app.main.service.user_service import set_cookie
from ..util.dto import AuthDTO

api = AuthDTO.api
user_auth = AuthDTO.user_auth


@api.route('/login')
class UserLogin(Resource):
    """
    User Login Resource
    """
    @api.doc('user login')
    @api.doc(responses={
        200: 'Successfully logged in.',
        401: 'Failed to log in.'
    })
    @api.expect(user_auth, validate=True)
    def post(self):
        # get the post data
        post_data = request.json

        @after_this_request
        def set_cookies(response):
            return set_cookie(response, post_data)
        return Auth.login_user(data=post_data)


@api.route('/logout')
class LogoutAPI(Resource):
    """
    Logout Resource
    """
    @api.doc('logout a user')
    @api.doc(responses={
        200: 'Successfully logged out user.',
        401: 'Token validation failed. User already logged out.'
    })
    def post(self):
        # get auth token
        auth_cookies = request.cookies
        return Auth.logout_user(data=auth_cookies)
