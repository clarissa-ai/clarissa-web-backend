from functools import wraps
from flask import request

from app.main.service.auth_helper import Auth


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        data, status = Auth.get_logged_in_user(request)
        data_status = data.get('status')
        if data_status == 'failure':
            return token_return_fail()
        kwargs['auth_object'] = {
            'auth_object': data,
            'resp_code': status
        }
        return f(*args, **kwargs)

    return decorated


def token_return_fail():
    return {
        'status': 'failure',
        'message': 'Failed to validate log in information.'
    }, 401
