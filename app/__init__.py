from flask import Flask


def register_blueprints(app):
    from app.onecity_v1 import v1_blueprint
    app.register_blueprint(
        v1_blueprint,
        url_prefix='/onecity/v1'
    )


def create_app():
    app = Flask(__name__, static_folder='./static')

    register_blueprints(app)

    return app
