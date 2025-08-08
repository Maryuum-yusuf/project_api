from flask import Blueprint, request, jsonify
from bson import ObjectId
from pymongo import MongoClient
from middlewares.auth_decorator import token_required, admin_required

client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
users = db["users"]

user_routes = Blueprint("user_routes", __name__)

@user_routes.route("/users/count", methods=["GET"])
@token_required
@admin_required
def count_users():
    total = users.count_documents({})
    return jsonify({"total_users": total})

# GET all users (admin only)
@user_routes.route("/users", methods=["GET"])
@token_required
@admin_required
def get_all_users():
    all_users = []
    for user in users.find():
        user["_id"] = str(user["_id"])
        user.pop("password", None)  # don't return password
        all_users.append(user)
    return jsonify(all_users)


# GET single user by ID
@user_routes.route("/users/<user_id>", methods=["GET"])
@token_required
def get_user_by_id(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return jsonify(user)


# PUT: Update user
@user_routes.route("/users/<user_id>", methods=["PUT"])
@token_required
def update_user(user_id):
    data = request.get_json()
    update_fields = {}

    for field in ["full_name", "email", "role", "is_suspended"]:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return jsonify({"error": "No data to update"}), 400

    result = users.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User updated successfully"})


# DELETE user
@user_routes.route("/users/<user_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_user(user_id):
    result = users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted successfully"})
