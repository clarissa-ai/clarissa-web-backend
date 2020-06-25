import os


# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    # UNCOMMENT THE LINE BELOW TO SWITCH BACK TO LOCAL SQLITE DB
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
    #     basedir,
    #     'clarissa_dev_main.db'
    # )
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:5432/postgres'.format(
        os.getenv('DEV_DB_USER'),
        os.getenv('DEV_DB_PWD'),
        os.getenv('DEV_DB_URL')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        basedir,
        'clarissa_test.db'
    )
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:5432/postgres'.format(
        os.getenv('RDS_DB_USER'),
        os.getenv('RDS_DB_PWD'),
        os.getenv('RDS_DB_URL')
    )


# Dictionary for retrieving correct config based on ENV variable
config_by_name = dict(
    DEV=DevelopmentConfig,
    TEST=TestingConfig,
    PRODUCTION=ProductionConfig
)

key = Config.SECRET_KEY
