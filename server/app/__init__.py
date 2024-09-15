from flask import Flask,request, make_response
from app.config import Config
from dotenv import load_dotenv
import os
from flask_redis import FlaskRedis
from flask_cors import CORS

redis_client = FlaskRedis()


def create_app(config_name=Config):
    load_dotenv()
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config.from_object(config_name)
    # print(app.config.get("REDIS_URL"))
    redis_client.init_app(app)
    
    # Set up CORS
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
    )

    with app.app_context():
        from app.routes.main import main_dp
        app.register_blueprint(main_dp)

    return app
