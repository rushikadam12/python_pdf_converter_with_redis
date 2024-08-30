from flask import Flask
from app.config import Config
from dotenv import load_dotenv
import os
from flask_redis import FlaskRedis

redis_client = FlaskRedis()


def create_app(config_name=Config):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_name)
    print(app.config.get("REDIS_URL"))
    redis_client.init_app(app)

    with app.app_context():
        from app.routes.main import main_dp

        app.register_blueprint(main_dp)

    return app
