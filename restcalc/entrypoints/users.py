from flask import Blueprint, request, jsonify
from restcalculator.service_layer import users_service
from restcalculator.schemas.schemas import UserSchema, PostUserSchema, UpdateUserSchema
from restcalculator.utils.hashoor import hash_password
from restcalculator.utils.auth_decos import role_required
from restcalculator.uow_factory import create_uow

users_blueprint = Blueprint("users", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
post_user_schema = PostUserSchema()
update_user_schema = UpdateUserSchema()

"""
You need to be an admin to create, see, delete and update users.
Does not make sense for users to be able to create other users.
"""


@users_blueprint.route("/users", methods=["POST"])
@role_required("admin")
def create_user():
    data = request.get_json()
    errors = post_user_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    user = post_user_schema.load(data)
    # Hash pw
    user.password = hash_password(user.password)
    with create_uow() as uow:
        user_id = users_service.add_user(user=user, uow=uow)
        uow.commit()
    with create_uow() as uow:
        user = users_service.get_user(user_id, uow)
        return jsonify(user_schema.dump(user)), 201


@users_blueprint.route("/users/<user_id>", methods=["GET"])
@role_required("admin")
def get_user(user_id):
    with create_uow() as uow:
        user = users_service.get_user(user_id, uow)
    return user_schema.dump(user), 200


@users_blueprint.route("/users", methods=["GET"])
@role_required("admin")
def list_users():
    with create_uow() as uow:
        try:
            users, pages = users_service.list_users(
                uow, request.args)
        except (ValueError, KeyError) as e:
            return jsonify({"message": f"Invalid filtering: {str(e)}"}), 400
        return jsonify({"total_pages": pages, "users": users_schema.dump(users)}), 200


@users_blueprint.route("/users/<user_id>", methods=["PATCH"])
@role_required("admin")
def update_user(user_id):
    data = request.get_json()
    errors = update_user_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    with create_uow() as uow:
        user_data = update_user_schema.load(data)
        users_service.update_user(user_id, uow, **user_data)
        uow.commit()
    return jsonify({"status": "success", "message": "User updated"}), 204


@users_blueprint.route("/users/<user_id>", methods=["DELETE"])
@role_required("admin")
def delete_user(user_id):
    with create_uow() as uow:
        users_service.delete_user(user_id, uow)
        uow.commit()
        return jsonify({"status": "success", "message": "User deleted"}), 200
