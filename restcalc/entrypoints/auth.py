from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, set_refresh_cookies
from restcalculator.service_layer import unit_of_work, users_service
from restcalculator.utils.hashoor import hash_password, check_password, is_password_valid
from restcalculator.utils.auth_decos import role_required
from flask import current_app as app
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone, timedelta
from restcalculator.schemas.schemas import AuthRegisterAdminSchema, AuthLoginSchema
from restcalculator.uow_factory import create_uow
from restcalculator.exceptions.custom_exceptions import UserExistsException

auth_blueprint = Blueprint("auth", __name__)

auth_login_schema = AuthLoginSchema()
auth_register_admin_schema = AuthRegisterAdminSchema()


@auth_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    errors = auth_login_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    with create_uow() as uow:
        user = users_service.get_user_by_email(email, uow)
        if user is None:
            # Check that the password meets the requirements
            if not is_password_valid(password):
                return jsonify({"status": "error", "message": "Password does not meet the requirements."}), 401
            # Register the user if they don't exist; use same schema as login
            user_obj = auth_login_schema.load(data)
            user_obj.password = hash_password(password)
            users_service.add_user(user_obj, uow)
            user = users_service.get_user_by_email(email, uow)
            uow.commit()
        # Verify the password
        if not check_password(password, user.password):
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401

        # Create the access token based on the user role.
        access_token = create_access_token(
            identity=user.id, additional_claims={"role": user.role, "email": user.email, "id": user.id})
        refresh_token = create_refresh_token(
            identity=user.id, additional_claims={"role": user.role, "email": user.email, "id": user.id})
        resp = jsonify(
            {"status": "success", "message": "Login successful."})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    resp = jsonify({"logout": True})
    unset_jwt_cookies(resp)
    return resp, 200


@auth_blueprint.after_app_request
def refresh_expiring_jwts(response):
    """Specific middleware decorator necessary to refresh expiring JWTs. """
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(seconds=300))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, get_jwt())
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@auth_blueprint.route("/refresh", methods=["GET"])
@jwt_required()
def get_csrf_refresh_token():
    """
    This is a prod workaround for a bug I found in production regarding browsers not setting the cookie. 
    """
    resp = jsonify({"csrf_token": get_jwt()["csrf"]})
    return resp, 200


@auth_blueprint.route("/admin", methods=["POST"])
def create_user():
    """This endpoint creates admin users. It is not meant to be used by the frontend.
    I did this in order to provide the functionality of creating admin users;
    however, the best approach would be to create it using the command line or 
    a separate admin panel that is protected. 
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    admin_password = data.get("admin_password")
    errors = auth_register_admin_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    # Validate password against session secret
    if admin_password != app.config["ADMIN_PASSWORD"]:
        return jsonify({"status": "error", "message": "Invalid password"}), 401
    with create_uow() as uow:
        users_service.add_admin(email, hash_password(password), uow)
        uow.commit()
        return jsonify({"status": "success", "message": "User created"}), 201
