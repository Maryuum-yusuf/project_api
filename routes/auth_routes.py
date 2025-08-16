from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
import re

bcrypt = Bcrypt()
auth_routes = Blueprint("auth_routes", __name__)

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
users = db["users"]

SECRET_KEY = os.getenv("SECRET_KEY", "sir_qarsoon")

def validate_somali_phone(phone):
    """Validate Somali phone number format"""
    # Remove spaces and special characters
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it starts with 252 (country code)
    if phone.startswith('252'):
        # Should be 12 digits total (252 + 9 digits)
        if len(phone) == 12 and phone[3:].isdigit():
            return True, phone
    
    # Check if it starts with +252
    if phone.startswith('+252'):
        # Should be 13 digits total (+252 + 9 digits)
        if len(phone) == 13 and phone[4:].isdigit():
            return True, phone
    
    # Check if it's just 9 digits (local format)
    if len(phone) == 9 and phone.isdigit():
        return True, f"252{phone}"
    
    return False, phone

def validate_name(name):
    """Validate name (no numbers allowed)"""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    
    # Check if name contains numbers
    if re.search(r'\d', name):
        return False, "Name cannot contain numbers"
    
    return True, name.strip()

def validate_password(password):
    """Validate password (minimum 6 characters)"""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    return True, password

@auth_routes.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    full_name = data.get("full_name")
    phone = data.get("phone")  # Changed from email to phone
    password = data.get("password")
    role = data.get("role", "user")  # default role 'user'

    if role not in ["user", "admin"]:
        return jsonify({"error": "Role must be 'user' or 'admin'"}), 400

    # Validate all fields are present
    if not full_name or not phone or not password:
        return jsonify({"error": "All fields are required"}), 400

    # Validate name (no numbers)
    name_valid, name_result = validate_name(full_name)
    if not name_valid:
        return jsonify({"error": name_result}), 400

    # Validate phone number
    phone_valid, phone_result = validate_somali_phone(phone)
    if not phone_valid:
        return jsonify({"error": "Invalid phone number format. Use Somali format: 252XXXXXXXXX or +252XXXXXXXXX or XXXXXXXXX (9 digits)"}), 400

    # Validate password (minimum 6 characters)
    password_valid, password_result = validate_password(password)
    if not password_valid:
        return jsonify({"error": password_result}), 400

    # Check if phone number already exists
    if users.find_one({"phone": phone_result}):
        return jsonify({"error": "Phone number already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    users.insert_one({
        "full_name": name_result,
        "phone": phone_result,  # Changed from email to phone
        "password": hashed_pw,
        "role": role,
        "is_suspended": False,
        "created_at": datetime.utcnow()
    })

    return jsonify({"message": "User registered successfully"}), 201

@auth_routes.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    phone = data.get("phone")  # Changed from email to phone
    password = data.get("password")

    # Validate phone number format
    phone_valid, phone_result = validate_somali_phone(phone)
    if not phone_valid:
        return jsonify({"error": "Invalid phone number format"}), 400

    user = users.find_one({"phone": phone_result})  # Changed from email to phone
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid phone number or password"}), 401

    if user.get("is_suspended", False):
        return jsonify({"error": "User is suspended"}), 403

    payload = {
        "user_id": str(user["_id"]),
        "phone": user["phone"],  # Changed from email to phone
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "token": token,
        "role": user["role"],
        "full_name": user["full_name"]
    })
