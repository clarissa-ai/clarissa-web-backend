import flask
import os

local_path = os.path.abspath(os.path.dirname(__file__))


def get_image(path):
    fullpath = local_path + "/../../resources/images/" + path
    contents = None
    with open(fullpath, 'rb') as f:
        contents = f.read()
    resp = flask.make_response(contents)
    resp.content_type = "image/jpeg"
    return resp
