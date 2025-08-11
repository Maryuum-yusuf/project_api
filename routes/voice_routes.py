from flask import Blueprint, jsonify, request
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from middlewares.auth_decorator import token_required
import base64
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
voice_recordings = db["voice_recordings"]

voice_routes = Blueprint("voice_routes", __name__)

@voice_routes.route("/voice/save", methods=["POST"])
@token_required
def save_voice_recording():
    """Save a voice recording for the authenticated user."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        data = request.get_json() or {}
        audio_data = data.get("audio_data")  # Base64 encoded audio
        duration = data.get("duration", 0)  # Duration in seconds
        language = data.get("language", "Somali")  # Language of speech
        transcription = data.get("transcription", "")  # Optional transcription
        
        if not audio_data:
            return jsonify({"error": "Audio data is required"}), 400

        # Create voice recording document
        recording_doc = {
            "user_id": ObjectId(user_id),
            "audio_data": audio_data,
            "duration": duration,
            "language": language,
            "transcription": transcription,
            "timestamp": datetime.utcnow(),
            "is_favorite": False
        }

        result = voice_recordings.insert_one(recording_doc)
        
        return jsonify({
            "message": "Voice recording saved successfully",
            "id": str(result.inserted_id),
            "timestamp": recording_doc["timestamp"].isoformat()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings", methods=["GET"])
@token_required
def get_voice_recordings():
    """Get all voice recordings for the authenticated user."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        recordings = list(voice_recordings.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1))
        
        for recording in recordings:
            recording["_id"] = str(recording["_id"])
            if isinstance(recording.get("user_id"), ObjectId):
                recording["user_id"] = str(recording["user_id"])
            if hasattr(recording.get("timestamp"), "isoformat"):
                recording["timestamp"] = recording["timestamp"].isoformat()

        return jsonify(recordings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>", methods=["GET"])
@token_required
def get_voice_recording(recording_id):
    """Get a specific voice recording by ID."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        recording = voice_recordings.find_one({
            "_id": ObjectId(recording_id),
            "user_id": ObjectId(user_id)
        })

        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        recording["_id"] = str(recording["_id"])
        if isinstance(recording.get("user_id"), ObjectId):
            recording["user_id"] = str(recording["user_id"])
        if hasattr(recording.get("timestamp"), "isoformat"):
            recording["timestamp"] = recording["timestamp"].isoformat()

        return jsonify(recording), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>/audio", methods=["GET"])
@token_required
def get_voice_audio(recording_id):
    """Get audio data for playback."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        recording = voice_recordings.find_one({
            "_id": ObjectId(recording_id),
            "user_id": ObjectId(user_id)
        })

        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        audio_data = recording.get("audio_data")
        if not audio_data:
            return jsonify({"error": "Audio data not found"}), 404

        # Convert base64 to audio bytes
        import base64
        try:
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            return jsonify({"error": f"Invalid audio data format: {str(e)}"}), 400

        # Return audio data with proper headers
        from flask import make_response
        response = make_response(audio_bytes)
        response.headers['Content-Type'] = 'audio/wav'  # Assuming WAV format
        response.headers['Content-Disposition'] = f'attachment; filename=recording_{recording_id}.wav'
        
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>/audio-data", methods=["GET"])
@token_required
def get_voice_audio_data(recording_id):
    """Get audio data as base64 for frontend playback."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        recording = voice_recordings.find_one({
            "_id": ObjectId(recording_id),
            "user_id": ObjectId(user_id)
        })

        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        audio_data = recording.get("audio_data")
        if not audio_data:
            return jsonify({"error": "Audio data not found"}), 404

        return jsonify({
            "audio_data": audio_data,
            "recording_id": recording_id,
            "duration": recording.get("duration", 0),
            "language": recording.get("language", "Somali"),
            "transcription": recording.get("transcription", ""),
            "timestamp": recording.get("timestamp").isoformat() if hasattr(recording.get("timestamp"), "isoformat") else str(recording.get("timestamp"))
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>", methods=["DELETE"])
@token_required
def delete_voice_recording(recording_id):
    """Delete a voice recording."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        result = voice_recordings.delete_one({
            "_id": ObjectId(recording_id),
            "user_id": ObjectId(user_id)
        })

        if result.deleted_count == 0:
            return jsonify({"error": "Recording not found"}), 404

        return jsonify({"message": "Voice recording deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>/favorite", methods=["POST"])
@token_required
def toggle_favorite_recording(recording_id):
    """Toggle favorite status of a voice recording."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        recording = voice_recordings.find_one({
            "_id": ObjectId(recording_id),
            "user_id": ObjectId(user_id)
        })

        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        new_favorite_status = not recording.get("is_favorite", False)
        
        result = voice_recordings.update_one(
            {"_id": ObjectId(recording_id), "user_id": ObjectId(user_id)},
            {"$set": {"is_favorite": new_favorite_status}}
        )

        if result.modified_count == 0:
            return jsonify({"error": "Failed to update recording"}), 500

        return jsonify({
            "message": "Favorite status updated",
            "is_favorite": new_favorite_status
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/favorites", methods=["GET"])
@token_required
def get_favorite_recordings():
    """Get all favorite voice recordings for the authenticated user."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        recordings = list(voice_recordings.find({
            "user_id": ObjectId(user_id),
            "is_favorite": True
        }).sort("timestamp", -1))
        
        for recording in recordings:
            recording["_id"] = str(recording["_id"])
            if isinstance(recording.get("user_id"), ObjectId):
                recording["user_id"] = str(recording["user_id"])
            if hasattr(recording.get("timestamp"), "isoformat"):
                recording["timestamp"] = recording["timestamp"].isoformat()

        return jsonify(recordings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings", methods=["DELETE"])
@token_required
def clear_all_recordings():
    """Delete all voice recordings for the authenticated user."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        result = voice_recordings.delete_many({"user_id": ObjectId(user_id)})
        
        return jsonify({
            "message": f"Deleted {result.deleted_count} recordings"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500