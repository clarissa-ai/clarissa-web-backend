# Import required libraries
import os
import datetime
import unittest
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# Import application factory and database
from app.main import create_app, db

# Import library to manage CORS
from flask_cors import CORS

# Import necessary models
from app.main.model import ( 
    user,
    blacklist,
    survey,
)

# Import API and Admin blueprints
from app import blueprint as app_blueprint
from app.admin import bp as admin_blueprint

# Get current environemnt from environment variable, defaults to dev
ENVIRONMENT_VAR = os.getenv('BOILERPLATE_ENV') or 'dev'

# Use application factory to create app based on environment
app = create_app(ENVIRONMENT_VAR)

# Register API and Admin blueprints to Flask app instance
app.register_blueprint(app_blueprint)
app.register_blueprint(admin_blueprint)

# Register CORS manager with app instance
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request

def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

app.app_context().push

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

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


@manager.command
def reset_dev():
    """Resets database, adds admin and test users, and any additional data (dev environment only)"""
    if ENVIRONMENT_VAR == 'dev':
        db.drop_all()
        db.create_all()
        admin_u = user.User(
            first_name = "ROOT",
            email = "testadmin@clarissa.ai",
            password = "test",
            admin = True,
            registered_on = datetime.datetime.utcnow()
        )
        db.session.add(admin_u)
        test_u = user.User(
            first_name = "Teo",
            email = "teo@clarissa.ai",
            password = "test",
            registered_on = datetime.datetime.utcnow()
        )
        db.session.add(test_u)
        covid_screening = survey.Survey(
            title = "COVID-19 Screening Tool",
            description = "Understand the next steps you can take to protect yourself and others against COVID-19. This short screening provides a recommendation to keep you healthy.",
            created_on = datetime.datetime.utcnow(),
            expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=50),
            active=True,
            main=True,
            author_id=1
        )
        db.session.add(covid_screening)
        q1 = survey.Question(
            title = "Have you experienced any of the following symptoms?",
            description = "Please select all the symptoms you have been experiencing.",
            type = "multiple_choice", 
            survey_id = covid_screening.id
        )
        covid_screening.root = q1
        db.session.add(covid_screening)
        db.session.add(q1)
        q2 = survey.Question(
            title = "Do you live in a state with a high density of COVID-19 cases?",
            description = "Please answer this Yes or No question.", 
            type = "multiple_choice", 
            survey_id = covid_screening.id
        )
        db.session.add(q2)
        db.session.commit()

# Always should be at end of file:
# actually runs the file when "python manage.py" is run from CLI
if __name__ == '__main__':
    manager.run()