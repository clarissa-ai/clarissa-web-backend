from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .config import config_by_name
import psutil
import os

db = SQLAlchemy()
flask_bcrypt = Bcrypt()
login_manager = LoginManager()


@login_manager.unauthorized_handler
def unauthorized_callback():
    curr_env = os.environ.get('DEPLOY_ENV', 'DEV')
    return redirect(url_for(
        'admin.login',
        _external=True,
        _scheme='https' if curr_env == 'PRODUCTION' else 'http'
    ))


def create_app(config_name):
    # initialize flask application
    app = Flask(__name__)
    # initialize configuratinos from config object based on environment
    app.config.from_object(config_by_name[config_name])
    # initialize app managers
    db.init_app(app)
    # initialize encryption manager
    flask_bcrypt.init_app(app)
    # initialize login manager for flask app
    login_manager.init_app(app)
    # start cpu utilization metrics
    psutil.cpu_percent(interval=1)
    return app
