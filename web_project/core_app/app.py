from flask import Flask
from .models import db
from .oauth2 import config_oauth
from .routes import bp_obj


def create_app(config=None):
    app = Flask(__name__)

    # load default configuration
    # app.config.from_object('core_app.settings')

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    setup_app(app)
    return app


def setup_app(app):
    # Create tables if they do not exist already
    @app.before_first_request
    def create_tables():
        db.create_all()

    db.init_app(app)
    config_oauth(app)
    app.register_blueprint(bp_obj, url_prefix='')
