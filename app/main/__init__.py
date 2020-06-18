from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from .config import config_by_name

db = SQLAlchemy()
flask_bcrypt = Bcrypt()
login_manager = LoginManager()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('admin.login'))


def create_app(config_name):
    app = Flask(__name__)
    # initialize configuratinos from config object based on environment
    app.config.from_object(config_by_name[config_name])
    # initialize app managers
    db.init_app(app)
    flask_bcrypt.init_app(app)
    login_manager.init_app(app)

    return app
