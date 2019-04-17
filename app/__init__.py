import logging.config
import os
from flask_migrate import Migrate
from flask import Flask

from app.models import db
from config import Config


basics_path = os.path.abspath(os.path.dirname(__file__))
migrate = Migrate()

def api_log_conf():
    if not os.path.exists('logs'):
        os.mkdir('logs')
    logging.config.fileConfig(os.path.join(basics_path, "logging.conf"))

def register_blueprints(app):
    from app.onecity_v1 import v1_blueprint
    app.register_blueprint(
        v1_blueprint,
        url_prefix='/onecity/v1'
    )


def create_app(config_class=Config):
    api_log_conf()
    app = Flask(__name__, static_folder='./static')
    app.config.from_object(config_class)


    db.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)
    return app


service_logger = logging.getLogger(name='service')
error_logger = logging.getLogger(name='error')
