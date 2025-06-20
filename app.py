import os
import zipfile
import gdown
from flask import Flask, request, jsonify
from transformers import MarianTokenizer, TFMarianMTModel

model_dir = "./amiin_model"

def download_model():
    if not os.path.exists(model_dir) or not os.listdir(model_dir):
        print("Downloading model...")
        os.makedirs(model_dir, exist_ok=True)
        file_id = "1hv3QH-WIMD47LRDSfALtBWg3tMEV1ZFH"
        url = f"https://drive.google.com/uc?id={file_id}"
        zip_path = os.path.join(model_dir, "model.zip")
        gdown.download(url, zip_path, quiet=False)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_dir)
        os.remove(zip_path)
        print("Model downloaded and extracted.")
    else:
        print("Model folder already exists and is not empty. Skipping download.")

download_model()

# Load tokenizer and model
tokenizer = MarianTokenizer.from_pretrained(model_dir, local_files_only=True)
model = TFMarianMTModel.from_pretrained(model_dir, local_files_only=True)

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
