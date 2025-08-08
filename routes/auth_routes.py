from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

bcrypt = Bcrypt()
auth_routes = Blueprint("auth_routes", __name__)

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
users = db["users"]

SECRET_KEY = os.getenv("SECRET_KEY", "sir_qarsoon")


@auth_routes.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")  # default role 'user'

    if role not in ["user", "admin"]:
        return jsonify({"error": "Role must be 'user' or 'admin'"}), 400

    if not full_name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if users.find_one({"email": email.lower()}):
        return jsonify({"error": "Email already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    users.insert_one({
        "full_name": full_name,
        "email": email.lower(),
        "password": hashed_pw,
        "role": role,
        "is_suspended": False,
        "created_at": datetime.utcnow()
    })

    return jsonify({"message": "User registered successfully"}), 201

@auth_routes.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users.find_one({"email": email.lower()})
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    if user.get("is_suspended", False):
        return jsonify({"error": "User is suspended"}), 403

    payload = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "token": token,
        "role": user["role"],
        "full_name": user["full_name"]
    })
