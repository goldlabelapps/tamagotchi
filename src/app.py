from flask import Flask
from flask_jwt_extended import JWTManager

from src.config import Config
from src.models import db
from src.routes.auth import auth_bp
from src.routes.pets import pets_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(pets_bp)

    with app.app_context():
        db.create_all()

    return app
