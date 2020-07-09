from app.main.model.user import User
from ..service.blacklist_service import save_token


class Auth:

    @staticmethod
    def login_user(data):
        try:
            # fetch the user data
            user = User.query.filter_by(email=data.get('email')).first()
            if user and user.check_password(data.get('password')):
                response_object = {
                    'status': 'success',
                    'message': 'Successfully logged in.'
                }
                return response_object, 200
            else:
                response_object = {
                    'status': 'failure',
                    'message': 'email or password does not match.'
                }
                return response_object, 401
        except Exception as e:
            print(e)
            response_object = {
                'status': 'failure',
                'message': 'Try again'
            }
            return response_object, 500

    @staticmethod
    def logout_user(data):
        if 'auth_token' in data.keys():
            auth_token = data['auth_token']
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                return save_token(token=auth_token)
            else:
                response_object = {
                    'status': 'failure',
                    'message': resp
                }
                return response_object, 401
        else:
            response_object = {
                'status': 'failure',
                'message': 'Provide a valid auth token.'
            }
            return response_object, 403

    @staticmethod
    def get_logged_in_user(new_request):
        # get the auth token
        auth_cookies = new_request.cookies
        if 'auth_token' in auth_cookies.keys():
            resp = User.decode_auth_token(auth_cookies['auth_token'])
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                response_object = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'birthdate': user.birthdate.strftime("%m/%d/%Y"),
                        'registered_on': user.registered_on.strftime(
                            "%m/%d/%Y %I:%M:%S%p"
                        ),
                        'sex': user.sex
                    }
                }
                return response_object, 200
            response_object = {
                'status': 'failure',
                'message': resp
            }
            return response_object, 401
        else:
            response_object = {
                'status': 'failure',
                'message': 'Provide a valid auth token.'
            }
            return response_object, 401
