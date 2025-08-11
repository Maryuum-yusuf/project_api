from flask import Blueprint, jsonify, request
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from middlewares.auth_decorator import token_required

client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
translations = db["translations"]

history_routes = Blueprint("history_routes", __name__)

@history_routes.route("/history", methods=["GET", "POST"])
@token_required
def list_history():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    if request.method == "POST":
        # POST: Add new translation to history
        data = request.get_json() or {}
        original_text = data.get("original_text")
        translated_text = data.get("translated_text")
        
        if not original_text or not translated_text:
            return jsonify({"error": "Missing original_text or translated_text"}), 400
        
        # Create new translation entry
        new_translation = {
            "user_id": ObjectId(user_id),
            "original_text": original_text,
            "translated_text": translated_text,
            "timestamp": datetime.utcnow(),
            "is_favorite": False
        }
        
        result = translations.insert_one(new_translation)
        new_translation["_id"] = str(result.inserted_id)
        
        return jsonify({
            "message": "Translation added to history",
            "translation": new_translation
        }), 201
    
    else:
        # GET: List user's translations
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        skip = (page - 1) * limit

        # Get user's translations
        user_translations = list(translations.find({"user_id": ObjectId(user_id)}).skip(skip).limit(limit).sort("timestamp", -1))
        total_translations = translations.count_documents({"user_id": ObjectId(user_id)})

        for trans in user_translations:
            trans["_id"] = str(trans["_id"])
            if isinstance(trans.get("user_id"), ObjectId):
                trans["user_id"] = str(trans["user_id"])
            if hasattr(trans.get("timestamp"), "isoformat"):
                trans["timestamp"] = trans["timestamp"].isoformat()

        return jsonify({
            "translations": user_translations,
            "total": total_translations,
            "page": page,
            "limit": limit,
            "pages": (total_translations + limit - 1) // limit
        })

@history_routes.route("/history/<translation_id>", methods=["DELETE"])
@token_required
def delete_history_item(translation_id):
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    res = translations.delete_one({"_id": ObjectId(translation_id), "user_id": ObjectId(user_id)})
    if res.deleted_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "deleted"})

@history_routes.route("/history", methods=["DELETE"])
@token_required
def clear_history():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    translations.delete_many({"user_id": ObjectId(user_id)})
    return jsonify({"message": "cleared"})

@history_routes.route("/history/<translation_id>", methods=["GET"])
@token_required
def get_history_item(translation_id):
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    translation = translations.find_one({"_id": ObjectId(translation_id), "user_id": ObjectId(user_id)})
    if not translation:
        return jsonify({"error": "Not found"}), 404

    translation["_id"] = str(translation["_id"])
    if isinstance(translation.get("user_id"), ObjectId):
        translation["user_id"] = str(translation["user_id"])
    if hasattr(translation.get("timestamp"), "isoformat"):
        translation["timestamp"] = translation["timestamp"].isoformat()

    return jsonify(translation)
