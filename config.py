from decouple import config
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api

from db import db
from resources.routes import routes


class DevelopmentConfig:
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:"
        f"{config('DB_PASSWORD')}"
        f"@localhost:{config('DB_PORT')}/"
        f"{config('DB_NAME')}"
    )


class ProductionConfig:
    FLASK_ENV = "prod"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:"
        f"{config('DB_PASSWORD')}"
        f"@localhost:{config('DB_PORT')}/"
        f"{config('DB_NAME')}"
    )


class TestingConfig:
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:"
        f"{config('DB_PASSWORD')}"
        f"@localhost:{config('DB_PORT')}/"
        f"{config('TEST_DB_NAME')}"
    )
    DEBUG = True


def create_app(config="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config)

    api = Api(app)
    migrate = Migrate(app, db)
    CORS(app)
    [api.add_resource(*route) for route in routes]
    return app
