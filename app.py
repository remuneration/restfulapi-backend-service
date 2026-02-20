import os
import redis

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from rq import Queue
from database import db

from resources import StoreBlueprint
from resources import ItemBlueprint
from resources import TagBlueprint
from resources import UserBlueprint


def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.redis_connection = redis.from_url(os.getenv("REDIS_URL"))
    app.heavy_queue = Queue("heavy_task", connection=app.redis_connection)


    @app.route("/healthcheck")
    def health_check():
        return {"status":"ok"}, 200

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "MY Stores API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return app.redis_connection.exists(f"bl:{jti}")

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message":"User logged out"}),
            401
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jtw_header,jtw_payload):
        return (
            jsonify({"message":"Token is not fresh"}),
            401
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message":"The token has expired"}),
            401
        )
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message":"Signature verification failed"}),
            401
        )
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({"message":"Request does not contain an access token"}),
            401
        )

    api = Api(app)

    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app