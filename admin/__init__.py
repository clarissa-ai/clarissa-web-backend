# admin/init.py

from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder="templates", static_folder="static")

from .routes import *