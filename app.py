from flask import Flask, request, jsonify
from transformers import MarianTokenizer, TFMarianMTModel
import tensorflow as tf

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
