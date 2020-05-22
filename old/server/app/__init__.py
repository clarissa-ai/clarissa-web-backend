from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

# Initialize Flask application instance with link to static react files and import configurations
app = Flask(__name__, static_folder="../../client/build/static", template_folder="../../client/build")
app.config.from_object(Config)

# Initialize SQLAlchemy instance and set up migration interface class
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize JWT token manager and RESTful Api instances
jwt = JWTManager(app)
api = Api(app)


# Import routes and api endpoints
from app import routes, resources, models

# Set up JWT token blacklister
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)
