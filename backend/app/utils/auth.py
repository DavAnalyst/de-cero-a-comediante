from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from ..models import User


def _decode_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, "Missing or malformed Authorization header"
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"],
        )
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload, error = _decode_token()
        if error:
            return jsonify({"error": error}), 401
        user = User.query.get(payload.get("sub"))
        if not user:
            return jsonify({"error": "User not found"}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload, error = _decode_token()
        if error:
            return jsonify({"error": error}), 401
        user = User.query.get(payload.get("sub"))
        if not user:
            return jsonify({"error": "User not found"}), 401
        if not user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated
