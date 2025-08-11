from flask import Blueprint, request, jsonify
from bson import ObjectId
from pymongo import MongoClient
from middlewares.auth_decorator import token_required, admin_required
from datetime import datetime, timedelta
import pytz

client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
users = db["users"]
translations = db["translations"]
favorites = db["favorites"]
voice_translations = db["voice_translations"]

user_routes = Blueprint("user_routes", __name__)

@user_routes.route("/users/count", methods=["GET"])
def count_users():
    total = users.count_documents({})
    return jsonify({"total_users": total})

# GET all users (admin only)
@user_routes.route("/users", methods=["GET"])
def get_all_users():
    all_users = []
    for user in users.find():
        user["_id"] = str(user["_id"])
        user.pop("password", None)  # don't return password
        all_users.append(user)
    return jsonify(all_users)


# GET single user by ID
@user_routes.route("/users/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return jsonify(user)


# PUT: Update user
@user_routes.route("/users/<user_id>", methods=["PUT"])
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
def delete_user(user_id):
    result = users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted successfully"})

# User-specific favorites (history moved to dedicated history_routes)

@user_routes.route("/user/favorites", methods=["GET"])
@token_required
def get_user_favorites():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403
    
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    skip = (page - 1) * limit
    
    # Get user's favorites
    user_favorites = list(favorites.find({"user_id": ObjectId(user_id)}).skip(skip).limit(limit).sort("timestamp", -1))
    total_favorites = favorites.count_documents({"user_id": ObjectId(user_id)})
    
    for fav in user_favorites:
        fav["_id"] = str(fav["_id"])
        if isinstance(fav.get("user_id"), ObjectId):
            fav["user_id"] = str(fav["user_id"])
        if isinstance(fav.get("translation_id"), ObjectId):
            fav["translation_id"] = str(fav["translation_id"])
        if hasattr(fav.get("timestamp"), "isoformat"):
            fav["timestamp"] = fav["timestamp"].isoformat()
    
    return jsonify({
        "favorites": user_favorites,
        "total": total_favorites,
        "page": page,
        "limit": limit,
        "pages": (total_favorites + limit - 1) // limit
    })

@user_routes.route("/user/stats", methods=["GET"])
@token_required
def get_user_stats():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403
    
    somalia_tz = pytz.timezone('Africa/Mogadishu')
    now = datetime.now(somalia_tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get user statistics
    total_translations = translations.count_documents({"user_id": ObjectId(user_id)})
    total_favorites = favorites.count_documents({"user_id": ObjectId(user_id)})
    total_voice_translations = voice_translations.count_documents({"user_id": ObjectId(user_id)})
    
    # Today's translations
    translations_today = translations.count_documents({
        "user_id": ObjectId(user_id),
        "timestamp": {"$gte": today_start.isoformat()}
    })
    
    # This week's translations
    translations_week = translations.count_documents({
        "user_id": ObjectId(user_id),
        "timestamp": {"$gte": week_start.isoformat()}
    })
    
    # This month's translations
    translations_month = translations.count_documents({
        "user_id": ObjectId(user_id),
        "timestamp": {"$gte": month_start.isoformat()}
    })
    
    return jsonify({
        "total_translations": total_translations,
        "total_favorites": total_favorites,
        "total_voice_translations": total_voice_translations,
        "translations_today": translations_today,
        "translations_week": translations_week,
        "translations_month": translations_month
    })
