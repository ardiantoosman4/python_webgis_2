from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from .config import Config
from .db import init_engine_and_session, remove_scoped_session
from flask_jwt_extended import JWTManager

def create_app():
    # Load .env before reading config

    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    # Init DB engine + scoped session
    init_engine_and_session(app.config["DATABASE_URL"])

    # JWT
    jwt = JWTManager(app)

    # Register blueprints
    from .auth import auth_bp
    from .views import views_bp
    from .edit import cms_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(cms_bp)

    # DB session lifecycle
    @app.teardown_appcontext
    def cleanup(exception=None):
        remove_scoped_session()

    return app
