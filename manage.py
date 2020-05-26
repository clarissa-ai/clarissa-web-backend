# Import required libraries
import os
import datetime
import unittest
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# Import application factory and database
from app.main import create_app, db

# Import necessary models
from app.main.model import user
from app.main.model import blacklist
from app.main.model import survey

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
        db.session.commit()

# Always should be at end of file:
# actually runs the file when "python manage.py" is run from CLI
if __name__ == '__main__':
    manager.run()