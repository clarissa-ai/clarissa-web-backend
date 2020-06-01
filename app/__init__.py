# app/__init__.py

from flask_restplus import Api
from flask import Blueprint

from .main.controller.user_controller import api as user_ns
from .main.controller.auth_controller import api as auth_ns
from .main.controller.survey_controller import api as survey_ns
from .main.controller.image_controller import api as image_ns

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='CLARISSA API REFERENCE',
          version='1.0',
          description='Documentation for Clarissa.ai API: a flask restplus web service'
        )

api.add_namespace(user_ns, path='/api/user')
api.add_namespace(auth_ns, path='/api')
api.add_namespace(survey_ns, path='/api/survey')
api.add_namespace(image_ns, path='/api/images')