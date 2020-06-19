import os
from ..model.survey import Survey, Link, Summary
from flask import make_response


def get_image(image_class, image_id, image_type):
    if image_class == "survey":
        return get_survey(image_id)
    elif image_class == "filler":
        return get_filler(image_id, image_type)
    elif image_class == "survey_link":
        return get_survey_link(image_id)
    elif image_class == "survey_summary":
        return get_survey_summary(image_id)
    else:
        resp_obj = {
            'status': 'failure',
            'message': 'Failed to fetch requested image.'
        }
        return resp_obj, 404


def get_survey(id):
    s = Survey.query.filter_by(id=id).first()
    if s and s.image_file:
        response = make_response(s.image_file)
        response.headers.set('Content-Type', 'image/{}'.format(s.image_type))
        response.headers.set(
            'Content-Disposition',
            'inline',
            filename='{}.{}'.format(s.id, s.image_type)
        )
        return response
    else:
        resp_obj = {
            'status': 'failure',
            'message': 'Failed to fetch requested image.'
        }
        return resp_obj, 404


def get_survey_link(id):
    s = Link.query.filter_by(id=id).first()
    if s and s.image_file:
        response = make_response(s.image_file)
        response.headers.set('Content-Type', 'image/{}'.format(s.image_type))
        response.headers.set(
            'Content-Disposition',
            'inline',
            filename='{}.{}'.format(s.id, s.image_type)
        )
        return response
    else:
        resp_obj = {
            'status': 'failure',
            'message': 'Failed to fetch requested image.'
        }
        return resp_obj, 404


def get_survey_summary(id):
    s = Summary.query.filter_by(id=id).first()
    if s and s.image_file:
        response = make_response(s.image_file)
        response.headers.set('Content-Type', 'image/{}'.format(s.image_type))
        response.headers.set(
            'Content-Disposition',
            'inline',
            filename='{}.{}'.format(s.id, s.image_type)
        )
        return response
    else:
        resp_obj = {
            'status': 'failure',
            'message': 'Failed to fetch requested image.'
        }
        return resp_obj, 404


local_path = os.path.abspath(os.path.dirname(__file__))


def get_filler(image_id, image_type):
    if image_id == "fill" and image_type == "png":
        full_path = local_path + "/fillers/fill.png"
        content = None
        with open(full_path, 'rb') as f:
            content = f.read()
        resp = make_response(content)
        resp.content_type = "image/png"
        return resp
    else:
        resp_obj = {
            'status': 'failure',
            'message': 'Failed to fetch requested filler.'
        }
        return resp_obj, 404
