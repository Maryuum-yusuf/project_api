from flask import Blueprint, jsonify, request, make_response, Response
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from middlewares.auth_decorator import token_required
from langdetect import detect
import base64
import gridfs

client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
voice_recordings = db["voice_recordings"]
fs = gridfs.GridFS(db)

voice_routes = Blueprint("voice_routes", __name__)

def parse_data_url_audio(data_url: str):
    """
    Parse data URL audio format
    data_url: 'data:audio/webm;codecs=opus;base64,AAAA...'
    return: (mime_type, raw_base64)
    """
    if not data_url.startswith("data:"):
        return None, None
    
    header, b64 = data_url.split(",", 1)
    # Example header: data:audio/webm;codecs=opus;base64
    if ";base64" not in header:
        return None, None
    
    mime_type = header.split(";")[0].replace("data:", "", 1)
    return mime_type, b64

def serialize_recording(recording):
    """
    Convert MongoDB document to JSON-serializable format
    """
    if recording:
        recording["_id"] = str(recording["_id"])
        if isinstance(recording.get("user_id"), ObjectId):
            recording["user_id"] = str(recording["user_id"])
        if isinstance(recording.get("file_id"), ObjectId):
            recording["file_id"] = str(recording["file_id"])
        if hasattr(recording.get("timestamp"), "isoformat"):
            recording["timestamp"] = recording["timestamp"].isoformat()
        # Ensure translation field is included
        if "translation" not in recording:
            recording["translation"] = ""
        # Remove audio_data if it exists (for old records)
        recording.pop("audio_data", None)
    return recording

@voice_routes.route("/voice/save", methods=["POST"])
@token_required
def save_voice_recording():
    """Save a voice recording for the authenticated user using GridFS."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        data = request.get_json() or {}
        audio_data = data.get("audio_data")  # data URL ama Base64
        duration = float(data.get("duration", 0))  # Duration in seconds
        language = data.get("language", "Somali")
        transcription = (data.get("transcription") or "").strip()
        translation = (data.get("translation") or "").strip()
        
        if not audio_data:
            return jsonify({"error": "Audio data is required"}), 400

        if not transcription:
            return jsonify({"error": "Transcription is required"}), 400

        # Detect language from transcription
        try:
            # Somali word list for better detection
            somali_words = {
                'waan', 'waxaan', 'waxay', 'wuxuu', 'waxaad', 'eedda', 'nin', 'naag', 'carruur', 'qof', 'dad',
                'bulsho', 'wadan', 'dalka', 'faraxsan', 'ku', 'faraxsanahay', 'mahadsanid', 'fadlan', 'waa',
                'ma', 'miyaa', 'wax', 'qoraal', 'cod', 'hadal', 'sheeg', 'dhig', 'samee', 'ka', 'la', 'iyo'
            }
            
            # Check if text contains Somali words
            text_words = transcription.lower().split()
            somali_word_count = sum(1 for word in text_words if word in somali_words)
            
            # If more than 30% of words are Somali, consider it Somali
            if somali_word_count > 0 and (somali_word_count / max(1, len(text_words))) > 0.3:
                detected_lang = "so"
            else:
                # Fallback to langdetect
                detected_lang = detect(transcription)
            
            if detected_lang != "so":
                return jsonify({"error": "Fadlan ku hadal Somali"}), 400
        except Exception as e:
            return jsonify({"error": "Waxaa dhacay khalad markii la hubinayay luqadda"}), 400

        # Auto-translate the transcription if no translation provided
        if not translation:
            try:
                # Use Google Translate API
                import requests
                url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=so&tl=en&dt=t&q={requests.utils.quote(transcription)}"
                response = requests.get(url)
                if response.status_code == 200:
                    data_translate = response.json()
                    translation = data_translate[0][0][0] if data_translate and data_translate[0] else ""
                else:
                    translation = ""
            except Exception as e:
                print(f"Translation error: {e}")
                translation = ""

        # Parse audio data (data URL or Base64)
        mime_type, b64 = parse_data_url_audio(audio_data) if audio_data.startswith("data:") else ("audio/wav", audio_data)
        if not b64:
            return jsonify({"error": "Invalid audio data (not data URL / base64)"}), 400

        # Decode and validate size (max 10MB)
        try:
            raw = base64.b64decode(b64)
        except Exception as e:
            return jsonify({"error": f"Invalid base64 data: {str(e)}"}), 400
        
        MAX_BYTES = 10 * 1024 * 1024  # 10MB
        if len(raw) > MAX_BYTES:
            return jsonify({"error": "Audio is too large (max 10MB)"}), 413

        # Generate filename with proper extension
        ext = {
            "audio/webm": "webm",
            "audio/ogg": "ogg", 
            "audio/mpeg": "mp3",
            "audio/wav": "wav",
            "audio/x-wav": "wav",
        }.get(mime_type, "bin")
        
        filename = f"rec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{ext}"

        # Save to GridFS
        grid_id = fs.put(
            raw,
            filename=filename,
            contentType=mime_type,
            user_id=str(user_id),
            duration=duration,
            created_at=datetime.utcnow(),
        )

        # Create compact document (no audio_data to keep DB lean)
        doc = {
            "user_id": ObjectId(user_id),
            "file_id": grid_id,
            "filename": filename,
            "mime_type": mime_type,
            "size_bytes": len(raw),
            "duration": duration,
            "language": language,
            "transcription": transcription,
            "translation": translation,
            "timestamp": datetime.utcnow(),
            "is_favorite": False,
        }
        
        result = voice_recordings.insert_one(doc)
        
        return jsonify({
            "message": "Voice recording saved successfully",
            "id": str(result.inserted_id),
            "file_id": str(grid_id),
            "mime_type": mime_type,
            "size_bytes": len(raw),
            "timestamp": doc["timestamp"].isoformat()
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
        
        # Serialize all recordings
        for recording in recordings:
            serialize_recording(recording)

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

        # Serialize recording
        serialize_recording(recording)

        return jsonify(recording), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>", methods=["PUT"])
@token_required
def update_voice_recording(recording_id):
    """Update a voice recording (e.g., translation)."""
    try:
        claims = getattr(request, "user", {}) or {}
        user_id = claims.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 403

        data = request.get_json() or {}
        
        # Only allow updating certain fields
        update_data = {}
        if "translation" in data:
            update_data["translation"] = data["translation"].strip()
        if "is_favorite" in data:
            update_data["is_favorite"] = bool(data["is_favorite"])

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        result = voice_recordings.update_one(
            {
                "_id": ObjectId(recording_id),
                "user_id": ObjectId(user_id)
            },
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Recording not found"}), 404

        return jsonify({
            "message": "Recording updated successfully",
            "modified_count": result.modified_count
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>/audio", methods=["GET"])
@token_required
def stream_voice_audio(recording_id):
    """Stream audio file with proper Content-Type headers."""
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

        file_id = recording.get("file_id")
        if not file_id:
            return jsonify({"error": "File missing"}), 404

        # Get file from GridFS
        grid_file = fs.get(ObjectId(file_id))
        data = grid_file.read()
        
        # Create response with proper headers
        resp = make_response(data)
        resp.headers["Content-Type"] = recording.get("mime_type", "application/octet-stream")
        resp.headers["Content-Length"] = str(len(data))
        resp.headers["Content-Disposition"] = f'inline; filename="{recording.get("filename", "audio.bin")}"'
        
        return resp

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>/audio-data", methods=["GET"])
@token_required
def get_voice_audio_data(recording_id):
    """Get audio data as base64 for frontend playback (for compatibility)."""
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

        file_id = recording.get("file_id")
        if not file_id:
            return jsonify({"error": "File missing"}), 404

        # Get file from GridFS and convert to base64
        grid_file = fs.get(ObjectId(file_id))
        data = grid_file.read()
        audio_data = base64.b64encode(data).decode('utf-8')

        return jsonify({
            "audio_data": audio_data,
            "recording_id": recording_id,
            "duration": recording.get("duration", 0),
            "language": recording.get("language", "Somali"),
            "transcription": recording.get("transcription", ""),
            "translation": recording.get("translation", ""),
            "timestamp": recording.get("timestamp").isoformat() if hasattr(recording.get("timestamp"), "isoformat") else str(recording.get("timestamp"))
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>/download", methods=["GET"])
@token_required
def download_voice_recording(recording_id):
    """Download voice recording as attachment."""
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

        file_id = recording.get("file_id")
        if not file_id:
            return jsonify({"error": "File missing"}), 404

        # Get file from GridFS
        grid_file = fs.get(ObjectId(file_id))
        data = grid_file.read()
        
        # Create response for download
        resp = make_response(data)
        resp.headers["Content-Type"] = recording.get("mime_type", "application/octet-stream")
        resp.headers["Content-Disposition"] = f'attachment; filename="{recording.get("filename", "recording.bin")}"'
        
        return resp

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>/save-local", methods=["POST"])
@token_required
def save_voice_recording_local(recording_id):
    """Save voice recording to local file system."""
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

        file_id = recording.get("file_id")
        if not file_id:
            return jsonify({"error": "File missing"}), 404

        # Get file from GridFS
        grid_file = fs.get(ObjectId(file_id))
        data = grid_file.read()

        # Create filename
        filename = recording.get("filename", f"recording_{recording_id}.bin")

        # Save to local file system
        import os
        output_dir = "downloads"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "wb") as f:
            f.write(data)

        return jsonify({
            "message": "Voice recording saved successfully",
            "filename": filename,
            "file_path": file_path,
            "file_size": len(data)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/recordings/<recording_id>", methods=["DELETE"])
@token_required
def delete_voice_recording(recording_id):
    """Delete a voice recording and its GridFS file."""
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

        # Delete GridFS file if it exists
        file_id = recording.get("file_id")
        if file_id:
            try:
                fs.delete(ObjectId(file_id))
            except Exception as e:
                print(f"Warning: Could not delete GridFS file {file_id}: {e}")

        # Delete recording document
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
        
        # Serialize all recordings
        for recording in recordings:
            serialize_recording(recording)

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

        # Get all recordings for user
        recordings = list(voice_recordings.find({"user_id": ObjectId(user_id)}))
        
        # Delete GridFS files
        for recording in recordings:
            file_id = recording.get("file_id")
            if file_id:
                try:
                    fs.delete(ObjectId(file_id))
                except Exception as e:
                    print(f"Warning: Could not delete GridFS file {file_id}: {e}")

        # Delete all recording documents
        result = voice_recordings.delete_many({"user_id": ObjectId(user_id)})
        
        return jsonify({
            "message": f"Deleted {result.deleted_count} recordings"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500