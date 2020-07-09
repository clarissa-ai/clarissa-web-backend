# app/__init__.py
import os
from flask_restplus import Api
from flask import Blueprint, url_for

from .main.controller.user_controller import api as user_ns
from .main.controller.auth_controller import api as auth_ns
from .main.controller.survey_controller import api as survey_ns
from .main.controller.image_controller import api as image_ns
from .main.controller.routes_controller import api as route_ns
from .main.controller.dashboard_controller import api as dashboard_ns
from .main.controller.illness_controller import api as illness_ns


blueprint = Blueprint('api', __name__)


if os.environ.get('DEPLOY_ENV') == 'PRODUCTION':
    @property
    def specs_url(self):
        return url_for(self.endpoint('specs'), _external=True, _scheme='https')
    Api.specs_url = specs_url

api = Api(
    blueprint,
    title='CLARISSA API REFERENCE',
    version='1.0',
    description='''Documentation for Clarissa.ai API:
                    A flask restplus web service'''
)


api.add_namespace(user_ns, path='/api/user')
api.add_namespace(auth_ns, path='/api')
api.add_namespace(survey_ns, path='/api/survey')
api.add_namespace(image_ns, path='/api/images')
api.add_namespace(route_ns, path='/api')
api.add_namespace(dashboard_ns, path='/api/dashboard')
api.add_namespace(illness_ns, path='/api/illness')
