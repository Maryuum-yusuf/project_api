from flask import Blueprint, jsonify, request
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from middlewares.auth_decorator import token_required
import os
from werkzeug.utils import secure_filename
import pytz
from routes.language_detection import somali_detector

client = MongoClient("mongodb://localhost:27017/")
db = client["somali_translator_db"]
voice_translations = db["voice_translations"]
translations = db["translations"]

voice_routes = Blueprint("voice_routes", __name__)



@voice_routes.route("/voice/translate", methods=["POST"])
@token_required
def voice_translate():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    # Check if audio file is present (recorded audio from frontend)
    if 'audio' not in request.files:
        return jsonify({"error": "No audio recording provided"}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No audio recording selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: wav, mp3, m4a, flac, ogg, webm"}), 400

    # Check if transcribed_text is provided (from frontend speech recognition)
    transcribed_text = request.form.get('transcribed_text')
    if not transcribed_text:
        return jsonify({"error": "No transcribed text provided. Please transcribe the audio first."}), 400

    try:
        # Save recorded audio file to database storage
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        # Detect language of the transcribed text
        language_detection = somali_detector.detect_text_language(transcribed_text)
        detected_language = language_detection['language']
        language_confidence = language_detection['confidence']
        detection_method = language_detection['method']

        # Check if the transcribed text is Somali - if not, return error message
        if detected_language != 'so' or language_confidence < 0.2:
            # Clean up file since we won't be using it
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({
                "error": "Qoraalka aad galisay ma aha afka Soomaaliga. Fadlan gali qoraal Soomaali ah.",
                "language_detection": {
                    "detected_language": detected_language,
                    "language_confidence": language_confidence,
                    "detection_method": detection_method,
                    "is_somali": False
                },
              
            }), 400

        # Translate Somali text
        from app import tokenizer, model
        inputs = tokenizer(transcribed_text, return_tensors="tf", padding=True, truncation=True)
        outputs = model.generate(**inputs)
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Define Somalia timezone
        somalia_tz = pytz.timezone('Africa/Mogadishu')

        # Save to voice_translations collection (both audio recording and translation)
        voice_entry = {
            "user_id": ObjectId(user_id),
            "audio_filename": unique_filename,
            "audio_path": file_path,
            "transcribed_text": transcribed_text,  # Text from frontend speech recognition
            "translated_text": translated_text,
            "timestamp": datetime.now(somalia_tz).isoformat(),
            "is_favorite": False,
            "detected_language": detected_language,
            "language_confidence": language_confidence,
            "detection_method": detection_method
        }
        
        result = voice_translations.insert_one(voice_entry)
        voice_entry["_id"] = str(result.inserted_id)

        # Also save to regular translations collection for consistency
        translation_entry = {
            "user_id": ObjectId(user_id),
            "original_text": transcribed_text,  # Transcribed text from frontend speech recognition
            "translated_text": translated_text,
            "timestamp": datetime.now(somalia_tz).isoformat(),
            "is_favorite": False,
            "source": "voice",
            "voice_translation_id": result.inserted_id
        }
        translations.insert_one(translation_entry)

        return jsonify({
            "message": "Voice recording and translation saved successfully",
            "voice_translation_id": str(result.inserted_id),
            "transcribed_text": transcribed_text,
            "translated_text": translated_text,
            "audio_filename": unique_filename,
            "language_detection": {
                "detected_language": detected_language,
                "language_confidence": language_confidence,
                "detection_method": detection_method,
                "is_somali": detected_language == 'so'
            }
        }), 200

    except Exception as e:
        # Clean up file if error occurred
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/voice/history", methods=["GET"])
@token_required
def get_voice_history():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    skip = (page - 1) * limit

    # Get user's voice translations
    user_voice_translations = list(voice_translations.find({"user_id": ObjectId(user_id)}).skip(skip).limit(limit).sort("timestamp", -1))
    total_voice_translations = voice_translations.count_documents({"user_id": ObjectId(user_id)})

    for trans in user_voice_translations:
        trans["_id"] = str(trans["_id"])
        if isinstance(trans.get("user_id"), ObjectId):
            trans["user_id"] = str(trans["user_id"])
        if hasattr(trans.get("timestamp"), "isoformat"):
            trans["timestamp"] = trans["timestamp"].isoformat()

    return jsonify({
        "voice_translations": user_voice_translations,
        "total": total_voice_translations,
        "page": page,
        "limit": limit,
        "pages": (total_voice_translations + limit - 1) // limit
    })

@voice_routes.route("/voice/<voice_id>", methods=["GET"])
@token_required
def get_voice_translation(voice_id):
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    voice_translation = voice_translations.find_one({"_id": ObjectId(voice_id), "user_id": ObjectId(user_id)})
    if not voice_translation:
        return jsonify({"error": "Voice translation not found"}), 404

    voice_translation["_id"] = str(voice_translation["_id"])
    if isinstance(voice_translation.get("user_id"), ObjectId):
        voice_translation["user_id"] = str(voice_translation["user_id"])
    if hasattr(voice_translation.get("timestamp"), "isoformat"):
        voice_translation["timestamp"] = voice_translation["timestamp"].isoformat()

    return jsonify(voice_translation)

@voice_routes.route("/voice/<voice_id>", methods=["DELETE"])
@token_required
def delete_voice_translation(voice_id):
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    # Get voice translation to delete audio file
    voice_translation = voice_translations.find_one({"_id": ObjectId(voice_id), "user_id": ObjectId(user_id)})
    if not voice_translation:
        return jsonify({"error": "Voice translation not found"}), 404

    # Delete audio file
    audio_path = voice_translation.get("audio_path")
    if audio_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except:
            pass  # Continue even if file deletion fails

    # Delete from database
    res = voice_translations.delete_one({"_id": ObjectId(voice_id), "user_id": ObjectId(user_id)})
    if res.deleted_count == 0:
        return jsonify({"error": "Not found"}), 404

    # Also delete from regular translations if it exists
    translations.delete_many({"voice_translation_id": ObjectId(voice_id)})

    return jsonify({"message": "Voice translation deleted successfully"})

@voice_routes.route("/voice", methods=["DELETE"])
@token_required
def clear_voice_history():
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    # Get all voice translations for this user
    user_voice_translations = list(voice_translations.find({"user_id": ObjectId(user_id)}))
    
    # Delete audio files
    for trans in user_voice_translations:
        audio_path = trans.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass

    # Delete from database
    voice_translations.delete_many({"user_id": ObjectId(user_id)})
    
    # Also delete from regular translations
    translations.delete_many({"user_id": ObjectId(user_id), "source": "voice"})

    return jsonify({"message": "Voice history cleared successfully"})

@voice_routes.route("/voice/<voice_id>/audio", methods=["GET"])
@token_required
def get_audio_file(voice_id):
    claims = getattr(request, "user", {}) or {}
    user_id = claims.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid token payload"}), 403

    voice_translation = voice_translations.find_one({"_id": ObjectId(voice_id), "user_id": ObjectId(user_id)})
    if not voice_translation:
        return jsonify({"error": "Voice translation not found"}), 404

    audio_path = voice_translation.get("audio_path")
    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error": "Audio file not found"}), 404

    # Return audio file
    from flask import send_file
    return send_file(audio_path, as_attachment=True, download_name=voice_translation.get("audio_filename", "audio.wav"))
