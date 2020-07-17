import sys
import os
import datetime
from app.main import create_app, db
from app.main.model import user, survey

# Get current environemnt from environment variable, defaults to dev
ENVIRONMENT_VAR = os.getenv('DEPLOY_ENV') or 'DEV'

# Use application factory to create app based on environment
app = create_app(ENVIRONMENT_VAR)


def run_migrations(env):
    ENV_STR = env[0]
    if ENV_STR == 'PREPROD' or ENV_STR == 'PREPRODUCTION':
        print('Starting migrations in Preprod environment')
        SCRIPT_RDS_DB_USER = os.environ.get('PREPROD_RDS_DB_USER')
        SCRIPT_RDS_DB_URL = os.environ.get('PREPROD_RDS_DB_URL')
        SCRIPT_RDS_DB_PWD = os.environ.get('PREPROD_RDS_DB_PWD')
        os.environ['DEPLOY_ENV'] = 'PRODUCTION'
        os.environ['RDS_DB_USER'] = SCRIPT_RDS_DB_USER
        os.environ['RDS_DB_URL'] = SCRIPT_RDS_DB_URL
        os.environ['RDS_DB_PWD'] = SCRIPT_RDS_DB_PWD
        print('Set environment variables for RDS_DB')
        stream = os.popen('python manage.py db upgrade')
        output = stream.read()
        print(output)
        print('Ran migrations on variables')
        os.environ['DEPLOY_ENV'] = 'DEV'
        os.environ['RDS_DB_USER'] = ' '
        os.environ['RDS_DB_URL'] = ' '
        os.environ['RDS_DB_PWD'] = ' '
        print('Returned environment variables to original state')
    elif ENV_STR == 'PRODUCTION' or ENV_STR == 'PROD':
        print('Starting migrations in Prod environment')
        SCRIPT_RDS_DB_USER = os.environ.get('PROD_RDS_DB_USER')
        SCRIPT_RDS_DB_URL = os.environ.get('PROD_RDS_DB_URL')
        SCRIPT_RDS_DB_PWD = os.environ.get('PROD_RDS_DB_PWD')
        os.environ['DEPLOY_ENV'] = 'PRODUCTION'
        os.environ['RDS_DB_USER'] = SCRIPT_RDS_DB_USER
        os.environ['RDS_DB_URL'] = SCRIPT_RDS_DB_URL
        os.environ['RDS_DB_PWD'] = SCRIPT_RDS_DB_PWD
        print('Set environment variables for RDS_DB')
        stream = os.popen('python manage.py db upgrade')
        output = stream.read()
        print(output)
        print('Ran migrations on variables')
        os.environ['DEPLOY_ENV'] = 'DEV'
        os.environ['RDS_DB_USER'] = ' '
        os.environ['RDS_DB_URL'] = ' '
        os.environ['RDS_DB_PWD'] = ' '
        print('Returned environment variables to original state')
    else:
        print('Requested environment doesn\'t exist')
        print('Please try again with a different environment name.')


def reset_dev():
    """Resets database, adds admin and test users, and any additional data
    (dev environment only)"""
    with app.app_context():
        if os.getenv('DEPLOY_ENV') == 'DEV':
            db.drop_all()
            db.create_all()
            # ADMIN USER
            admin_u = user.AdminUser(
                username="Admin McAdminson",
                email="admin@clarissa.ai",
                password="test",
                registered_on=datetime.datetime.utcnow()
            )
            db.session.add(admin_u)
            db.session.commit()
            # TEST USER
            test_u = user.User(
                first_name="Teo",
                email="teo@clarissa.ai",
                password="test",
                registered_on=datetime.datetime.utcnow()
            )
            db.session.add(test_u)
            db.session.commit()
            # COVID SCREENING
            covid_screening = survey.Survey(
                title="COVID-19 Screening Tool",
                description=('Understand the next steps you can take to '
                             'protect yourself and others against COVID-19.'
                             ' This short screening provides a recommendation'
                             ' to keep you healthy.'),
                created_on=datetime.datetime.utcnow(),
                expiration_date=datetime.datetime.utcnow() +  datetime.timedelta(days=50), # noqa E501
                active=True,
                main=True,
                author_id=admin_u.id
            )
            db.session.add(covid_screening)
            db.session.commit()
            # COVID SCREENING QUESTIONS
            q1 = survey.Question(
                title="Have you experienced any of the following symptoms?",
                description=("Please select all the symptoms "
                             "you have been experiencing."),
                type="multiple_select",
                survey_id=covid_screening.id
            )
            db.session.add(q1)
            db.session.commit()
            covid_screening.root_id = q1.id
            q2 = survey.Question(
                title="Do you live in a state with a high density of COVID-19 cases?", # noqa E501
                description="Please answer this yes or no question.",
                type="single_select",
                survey_id=covid_screening.id
            )
            db.session.add(q2)
            db.session.add(covid_screening)
            db.session.commit()
            # LINKS
            l1 = survey.Link(
                title="Disenfect Surfaces",
                description="Information about hand-washing, physical distancing, isolating from others, and more.", # noqa E501
                link="https://www.cdc.gov/coronavirus/2019-ncov/index.html",
                survey_id=covid_screening.id
            )
            l2 = survey.Link(
                title="Wash your Hands",
                description="Information about hand-washing, physical distancing, isolating from others, and more.", # noqa E501
                link="https://www.cdc.gov/coronavirus/2019-ncov/index.html",
                survey_id=covid_screening.id
            )
            l3 = survey.Link(
                title="Wear a Mask",
                description="Information about hand-washing, physical distancing, isolating from others, and more.", # noqa E501
                link="https://www.cdc.gov/coronavirus/2019-ncov/index.html",
                survey_id=covid_screening.id
            )
            l4 = survey.Link(
                title="Adhere to Social Distancing",
                description="Information about hand-washing, physical distancing, isolating from others, and more.", # noqa E501
                link="https://www.cdc.gov/coronavirus/2019-ncov/index.html",
                survey_id=covid_screening.id
            )
            db.session.add(l1)
            db.session.add(l2)
            db.session.add(l3)
            db.session.add(l4)
            db.session.commit()


if __name__ == "__main__":
    cli_args = sys.argv
    if len(cli_args) > 2:
        locals()[cli_args[1]](cli_args[2:])
    else:
        locals()[cli_args[1]]()
