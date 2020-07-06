import datetime
import os
from app.main import db
from app.main.model.user import User

curr_env = os.environ.get('DEPLOY_ENV', 'DEV')
cookie_secure = curr_env == 'PRODUCTION'


def save_new_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        new_user = User(
            email=data['email'],
            first_name=data['first_name'],
            password=data['password'],
            registered_on=datetime.datetime.utcnow(),
            birthdate=datetime.date.strptime(data['birthdate'], "%m/%d/%Y")
        )
        save_changes(new_user)
        return register_user(new_user)
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please log in.',
        }
        return response_object, 409


def set_cookie(response, data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return response
    elif user.check_password(data['password']):
        token = user.encode_auth_token(user.id)
        response.set_cookie(
            'auth_token', value=token,
            secure=cookie_secure,
            httponly=True
        )
        return response
    return response


def get_all_users():
    return {
        'users': User.query.all(),
        'status': 'success'
    }, 200


def get_user_by_id(id):
    return User.query.filter_by(id=id).first()


def save_changes(data):
    db.session.add(data)
    db.session.commit()


def register_user(user):
    try:
        response_object = {
            'status': 'success',
            'message': 'Successfully registered.'
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'An error occurred. Please try again.'
        }
        print(e)
        return response_object, 401
