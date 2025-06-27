import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import MarianTokenizer, TFMarianMTModel
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)


db = SQLAlchemy(app)

# 📦 Load model
model_dir = "./amiin_model"
tokenizer = MarianTokenizer.from_pretrained(model_dir, local_files_only=True)
model = TFMarianMTModel.from_pretrained(model_dir, local_files_only=True)

# 📄 Translation Model
class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    translated_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "original_text": self.original_text,
            "translated_text": self.translated_text,
            "timestamp": self.timestamp.isoformat(),
            "is_favorite": self.is_favorite
        }

# 🔁 Translate route
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

        # Save to history
        new_entry = Translation(
            original_text=input_text,
            translated_text=translated_text
        )
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"translation": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📜 Get all history
@app.route("/history", methods=["GET"])
def get_history():
    entries = Translation.query.order_by(Translation.timestamp.desc()).all()
    return jsonify([entry.to_dict() for entry in entries])

# 🌟 Mark favorite
@app.route("/favorite", methods=["POST"])
def mark_favorite():
    data = request.get_json()
    entry_id = data.get("id")

    entry = Translation.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Translation not found"}), 404

    entry.is_favorite = True
    db.session.commit()
    return jsonify({"message": "Marked as favorite"})

# ⭐ Get all favorites
@app.route("/favorites", methods=["GET"])
def get_favorites():
    entries = Translation.query.filter_by(is_favorite=True).order_by(Translation.timestamp.desc()).all()
    return jsonify([entry.to_dict() for entry in entries])


# 🗑️ Delete single history item
@app.route("/history/<int:entry_id>", methods=["DELETE"])
def delete_history(entry_id):
    entry = Translation.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Translation not found"}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# 🗑️ Delete all histor

@app.route("/history", methods=["DELETE"])
def delete_all_history():
    db.session.query(Translation).delete()
    db.session.commit()
    return jsonify({"message": "All history deleted"})

# 🗑️ Delete all favorite
@app.route("/favorites", methods=["DELETE"])
def delete_all_favorites():
    db.session.query(Translation).filter_by(is_favorite=True).delete()
    db.session.commit()
    return jsonify({"message": "All favorites deleted"})

# 🗑️ Delete single favorites
@app.route("/favorites/<int:entry_id>", methods=["DELETE"])
def delete_favorite(entry_id):      
    entry = Translation.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Translation not found"}), 404
    entry.is_favorite = False
    db.session.commit()
    return jsonify({"message": "Removed from favorites"})

# ✅ Initialize


    # ✅ Samee database table marka app la bilaabo
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "App-ka Somali Translator wuu socdaa 🎉"


# ✅ Local only: Orod server Flask haddii file-ka si toos ah loo ordayo
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

