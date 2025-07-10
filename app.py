import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import MarianTokenizer, TFMarianMTModel
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ✅ MongoDB setup
mongo_uri = "mongodb+srv://maryama:1234@cluster0.stv0d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["somali_translator_db"]
translations = db["translations"]

# ✅ Load translation model
model_dir = "./amiin_model"
tokenizer = MarianTokenizer.from_pretrained(model_dir, local_files_only=True)
model = TFMarianMTModel.from_pretrained(model_dir, local_files_only=True)

@app.route("/")
def home():
    return "🚀 Somali Translator API waa socda oo MongoDB waa ku xiran!"

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    input_text = data.get("text", "")

    if not input_text.strip():
        return jsonify({"translation": "No input text provided."})

    try:
        inputs = tokenizer(input_text, return_tensors="tf", padding=True, truncation=True)
        outputs = model.generate(**inputs)
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # ✅ Save to MongoDB
        new_entry = {
            "original_text": input_text,
            "translated_text": translated_text,
            "timestamp": datetime.utcnow(),
            "is_favorite": False
        }
        result = translations.insert_one(new_entry)
        new_entry["_id"] = str(result.inserted_id)

        return jsonify({"translation": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def get_history():
    docs = list(translations.find().sort("timestamp", -1))
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        doc["timestamp"] = doc["timestamp"].isoformat()
    return jsonify(docs)

@app.route("/favorite", methods=["POST"])
def mark_favorite():
    data = request.get_json()
    entry_id = data.get("id")
    from bson import ObjectId
    result = translations.update_one({"_id": ObjectId(entry_id)}, {"$set": {"is_favorite": True}})
    if result.modified_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Marked as favorite"})

@app.route("/favorites", methods=["GET"])
def get_favorites():
    docs = list(translations.find({"is_favorite": True}).sort("timestamp", -1))
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        doc["timestamp"] = doc["timestamp"].isoformat()
    return jsonify(docs)

@app.route("/history/<entry_id>", methods=["DELETE"])
def delete_history(entry_id):
    from bson import ObjectId
    result = translations.delete_one({"_id": ObjectId(entry_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"})

@app.route("/history", methods=["DELETE"])
def delete_all_history():
    translations.delete_many({})
    return jsonify({"message": "All history deleted"})

@app.route("/favorites", methods=["DELETE"])
def delete_all_favorites():
    translations.update_many({"is_favorite": True}, {"$set": {"is_favorite": False}})
    return jsonify({"message": "All favorites unmarked"})

@app.route("/favorites/<entry_id>", methods=["DELETE"])
def delete_favorite(entry_id):
    from bson import ObjectId
    result = translations.update_one({"_id": ObjectId(entry_id)}, {"$set": {"is_favorite": False}})
    if result.matched_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Removed from favorites"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# Load the model from local folder
model_path = "./amiin_model"
tokenizer = MarianTokenizer.from_pretrained(model_path)
model = TFMarianMTModel.from_pretrained(model_path)

# Setup Flask
app = Flask(__name__)

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    input_text = data["text"]
    inputs = tokenizer(input_text, return_tensors="tf", padding=True, truncation=True)
    outputs = model.generate(**inputs)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"translation": translated_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

