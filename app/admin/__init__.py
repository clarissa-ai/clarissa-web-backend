# admin/init.py

from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin', static_folder="static", template_folder="templates")

from .routes import *