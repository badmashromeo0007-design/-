import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Initialize Gemini API securely using environment variable
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if not api_key:
        return jsonify({"error": "Gemini API key configured nahi hai!"}), 500
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"error": "Prompt zaroori hai!"}), 400

    try:
        # Updated to use the correct available model
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            f"Act as a 3D Cinematic Audio Drama Director. Create a high-intensity, dramatic script/dialogue for SUPER YODDHA (सुपर योद्धा) based on this concept: {prompt}"
        )
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
