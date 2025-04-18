from flask import Flask, request, jsonify
import google.generativeai as genai
from PIL import Image
import base64
from io import BytesIO
import os

app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

@app.route('/extract-text', methods=['POST'])
def extract_text():
    if 'image' not in request.files:
        return jsonify({"error": "画像ファイルが見つかりません"}), 400

    file = request.files['image']
    image = Image.open(file.stream)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    prompt = "この画像に記載されているすべての文字、記号、英数字を忠実に抽出してください。構造や配置を保持し、創作や補完はしないでください。"

    try:
        response = model.generate_content(
            contents=[{
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_base64
                        }
                    }
                ]
            }]
        )
        return jsonify({"text": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '🎉 Gemini OCR API is running! Use POST /extract-text to send an image.'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)