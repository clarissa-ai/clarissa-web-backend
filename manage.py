# Import required libraries
import os
import unittest
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# Import application factory and database
from app.main import create_app, db

# Import library to manage CORS
from flask_cors import CORS

# Import API and Admin blueprints
from app import blueprint as app_blueprint
from app.admin import admin_bp as admin_blueprint

from app.main.app_init_utilities import root_user_setup

# from werkzeug.middleware.proxy_fix import ProxyFix
from flask import _request_ctx_stack

# Get current environemnt from environment variable, defaults to dev
ENVIRONMENT_VAR = os.getenv('DEPLOY_ENV') or 'DEV'

# Use application factory to create app based on environment
app = create_app(ENVIRONMENT_VAR)

# if ENVIRONMENT_VAR == 'PRODUCTION':
#     app = ProxyFix(app)

# Register API and Admin blueprints to Flask app instance
app.register_blueprint(admin_blueprint)
app.register_blueprint(app_blueprint)

# Register CORS manager with app instance
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def _force_https():
    # my local dev is set on debug, but on AWS it's not (obviously)
    # I don't need HTTPS on local, change this to whatever condition you want.
    if ENVIRONMENT_VAR == 'PRODUCTION':
        if _request_ctx_stack is not None:
            reqctx = _request_ctx_stack.top
            reqctx.url_adapter.url_scheme = 'https'


app.before_request(_force_https)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization'
    )
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response


app.app_context().push

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

with app.app_context():
    root_user_setup(db, ENVIRONMENT_VAR)


@manager.command
def run():
    '''Runs Flask Application'''
    app.run(host="0.0.0.0")


@manager.command
def test():
    """Runs all unit tests"""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


# Always should be at end of file:
# actually runs the file when "python manage.py" is run from CLI
# (Like Java's SPVM)
if __name__ == '__main__':
    manager.run()
