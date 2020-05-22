import datetime

from app.main import db
from app.main.model.user import User 


def save_new_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        new_user = User(
            email = data['email'],
            first_name = data['first_name'],
            password = data['password'],
            registered_on=datetime.datetime.utcnow(),
        )
        save_changes(new_user)
        response_object = {
            'status': 'success',
            'message': 'Successfully',
        }
        return generate_token(new_user)
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please log in.',
        }
        return response_object, 409

def get_all_users():
    return User.query.all()

def get_user_by_id(id):
    return User.query.filter_by(id=id).first()

def save_changes(data):
    db.session.add(data)
    db.session.commit()

def generate_token(user):
    try:
        # generate the auth token
        auth_token = user.encode_auth_token(user.id)
        response_object = {
            'status': 'success',
            'message': 'Successfully registered.',
            'Authorization': auth_token.decode()
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'An error occurred. Please try again.'
        }
        return response_object, 401