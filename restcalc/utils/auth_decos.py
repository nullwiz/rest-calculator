from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


def role_required(role):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            # Access the JWT claims to get the user's role
            claims = get_jwt()
            user_role = claims.get("role", "")

            if user_role != role:
                return jsonify({"status": "error", "message": "Unauthorized access"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def is_admin():
    claims = get_jwt()
    user_role = claims.get("role", "")
    return user_role == "admin"


def get_user_id():
    claims = get_jwt()
    user_id = claims.get("id", "")
    return user_id
