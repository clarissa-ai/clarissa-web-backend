# admin/init.py
from flask import Blueprint

admin_bp = Blueprint(
    'admin', __name__,
    url_prefix='/admin',
    static_folder="static",
    template_folder="templates"
)

# Added a comment to ignore import errors on this line
from .routes import *  # noqa: E402,F401,F403
