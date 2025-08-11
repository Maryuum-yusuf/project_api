from flask import Blueprint, jsonify, request
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from middlewares.auth_decorator import token_required

client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
favorites = db["favorites"]
translations = db["translations"]

favorites_routes = Blueprint("favorites_routes", __name__)

@favorites_routes.route("/favorite", methods=["POST"])
@token_required
def add_favorite():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    data = request.get_json() or {}
    hist_id = data.get("id")
    original_text = data.get("original_text")
    translated_text = data.get("translated_text")

    doc = None
    if hist_id:
        h = translations.find_one({"_id": ObjectId(hist_id)})
        if h:
            doc = {
                "user_id": ObjectId(user_id),
                "original_text": h.get("original_text", ""),
                "translated_text": h.get("translated_text", ""),
                "is_favorite": True,
                "timestamp": datetime.utcnow(),
                "translation_id": h["_id"],
            }
    if not doc:
        if not original_text or not translated_text:
            return jsonify({"error": "Missing original_text/translated_text"}), 400
        doc = {
            "user_id": ObjectId(user_id),
            "original_text": original_text,
            "translated_text": translated_text,
            "is_favorite": True,
            "timestamp": datetime.utcnow(),
        }

    res = favorites.insert_one(doc)
    return jsonify({"message": "ok", "id": str(res.inserted_id)}), 200

@favorites_routes.route("/favorites", methods=["GET"])
@token_required
def list_favorites():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    items = list(favorites.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1))
    for it in items:
        it["_id"] = str(it["_id"])
        if isinstance(it.get("user_id"), ObjectId):
            it["user_id"] = str(it["user_id"])
        if isinstance(it.get("translation_id"), ObjectId):
            it["translation_id"] = str(it["translation_id"])
        if hasattr(it.get("timestamp"), "isoformat"):
            it["timestamp"] = it["timestamp"].isoformat()
    return jsonify(items)

@favorites_routes.route("/favorites/<fav_id>", methods=["DELETE"])
@token_required
def delete_favorite(fav_id):
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    res = favorites.delete_one({"_id": ObjectId(fav_id), "user_id": ObjectId(user_id)})
    if res.deleted_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "deleted"})

@favorites_routes.route("/favorites", methods=["DELETE"])
@token_required
def clear_favorites():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    favorites.delete_many({"user_id": ObjectId(user_id)})
    return jsonify({"message": "cleared"})
