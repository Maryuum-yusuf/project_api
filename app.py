import os
import requests
import zipfile
from flask import Flask, request, jsonify
from transformers import MarianTokenizer, TFMarianMTModel
from pathlib import Path

# Set model directory
model_dir = "./amiin_model"

# Function to download and unzip model
def download_model():
    if not os.path.exists(model_dir) or not os.listdir(model_dir):
        print("Downloading model...")
        os.makedirs(model_dir, exist_ok=True)
        # Link to the zipped model on Google Drive
        url = "https://drive.google.com/uc?export=download&id=1hv3QH-WIMD47LRDSfALtBWg3tMEV1ZFH"
        zip_path = os.path.join(model_dir, "model.zip")
        r = requests.get(url)
        with open(zip_path, "wb") as f:
            f.write(r.content)
        # Unzip the model
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_dir)
        os.remove(zip_path)
        print("Model downloaded and extracted.")
    else:
        print("Model folder already exists and is not empty. Skipping download.")

# Download model if needed
download_model()

# Prepare tokenizer paths
source_spm = str(Path(model_dir) / "source.spm")
target_spm = str(Path(model_dir) / "target.spm")

# Load tokenizer manually (disable fallback)
tokenizer = MarianTokenizer(
    source_spm=source_spm,
    target_spm=target_spm,
    tokenizer_file=None  # Important to avoid fallback error
)

# Load the TensorFlow model
model = TFMarianMTModel.from_pretrained(model_dir, local_files_only=True)

# Setup Flask app
app = Flask(__name__)

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    input_text = data["text"]
    inputs = tokenizer(input_text, return_tensors="tf", padding=True, truncation=True)
    outputs = model.generate(**inputs)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"translation": translated_text})

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
