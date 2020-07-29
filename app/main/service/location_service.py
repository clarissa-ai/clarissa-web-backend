import json
import os
import datetime
from app.main.model.user import User
from app.main.model.location import Location
from app.main import db


CURR_PATH = os.path.dirname(os.path.realpath(__file__))
NYU_LOC_FILE_PATH = os.path.join(
    CURR_PATH,
    'resources/location_service/NYU.json'
)


def get_nyu_locations():
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved NYU locations list.',
        'locations': ''
    }
    with open(NYU_LOC_FILE_PATH, 'r') as nyu_loc_json:
        response_object['locations'] = json.loads(nyu_loc_json.read())
    return response_object, 200


def get_location_history(user_id):
    response_object = {
        'status': 'success',
        'message': 'Successfully retrieved user\'s location history.',
        'locations': []
    }
    u = User.query.filter_by(id=user_id).first()
    for location in u.locations:
        response_object['locations'].append(location.get_json())
    return response_object, 200


def add_location(user_id, name, date):
    response_object = {
        'status': 'success',
        'message': 'Successfully added location to user\'s location history'
    }
    loc = Location(
        created_on=datetime.datetime.now(
        ) if not date else datetime.datetime.strptime(
                date,
                "%Y-%m-%dT%H:%M:%S.000Z"
        ),
        name=name,
        user_id=user_id
    )
    db.session.add(loc)
    db.session.commit()
    return response_object, 200
