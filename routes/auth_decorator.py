from functools import wraps
from flask import request, jsonify, g
import jwt, os

SECRET_KEY = os.getenv("SECRET_KEY", "sir_qarsoon")
BYPASS_AUTH = os.getenv("BYPASS_AUTH") == "true"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if BYPASS_AUTH:
            g.current_user = {"role": "admin", "email": "dev@example.com"}
            return f(*args, **kwargs)
        token = None
        auth = request.headers.get("Authorization", "")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
        if not token:
            token = request.headers.get("x-access-token") or request.args.get("token") \
                    or request.cookies.get("authToken") or request.cookies.get("token")
        if not token:
            return jsonify({"error": "Token is missing"}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 403
        g.current_user = data
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if BYPASS_AUTH:
            return f(*args, **kwargs)
        user = getattr(g, "current_user", None)
        role = (user.get("role") or "").lower() if user else ""
        if role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated