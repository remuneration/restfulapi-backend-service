from datetime import timedelta
import os

from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import create_access_token,create_refresh_token, get_jwt_identity, get_jwt
from flask_jwt_extended import jwt_required
from passlib.hash import pbkdf2_sha256
from flask import current_app


from models import UserModel
from schemas import UserSchema, Administrator
from database import db
from admin import admin_required

blp = Blueprint("users", __name__, description="Operations with users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.user_name == user_data["user_name"]).first():
            abort(409, message="Username is already exist")

        user = UserModel(user_name=user_data["user_name"],
                         user_password=pbkdf2_sha256.hash(user_data["user_password"])
                         )
        db.session.add(user)
        db.session.commit()

        return {"message":"User was created"}, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.user_name == user_data["user_name"]).first()

        if user and pbkdf2_sha256.verify(user_data["user_password"], user.user_password):
            access_token = create_access_token(identity=str(user.user_id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.user_id))
            return {"access_token": access_token, "refresh_token": refresh_token}

        abort(401, message="Invalid Credentials")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False, expires_delta=timedelta(minutes=10))
        return {"non_fresh_token":new_token}

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        current_app.redis_connection.set(f"bl:{jti}", "", ex=600)
        return {"message":"Logged out"}


@blp.route("/user/<int:user_id>")
class User(MethodView):

    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @admin_required
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()

        return {"message":"User was deleted"}, 200

@blp.route("/admin/rights")
class AdminRights(MethodView):
    @jwt_required()
    @blp.arguments(Administrator)
    def post(self, user_data):
        current_user = get_jwt_identity()
        check_user = UserModel.query.get_or_404(current_user)

        if check_user.admin_access or user_data.get("admin_password") == os.getenv("ADMIN_PASSWORD"):
            user = UserModel.query.filter_by(user_name=user_data["user_name"]).first()

            user.admin_access = True
            db.session.commit()
            return {"message":f"{user.user_name} is now admin"}, 201

        return {"message":"Admin access required"}

