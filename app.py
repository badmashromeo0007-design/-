import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Render ya environment se API Key automatic uthane ke liye
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Model ko configure karein (updated model name)
model = genai.GenerativeModel("models/gemini-3.8-flash")

@app.route('/')
def home():
    return "Super Yoddha Studio API is running!"

@app.route('/generate-script', methods=['POST'])
def generate_script():
    try:
        data = request.get_json()
        concept = data.get('concept', '')
        chapter_no = data.get('chapter_no', '1')
        chapter_title = data.get('chapter_title', '')
        system_name = data.get('system_name', '')
        dhruv_rank = data.get('dhruv_rank', '')

        # Gemini ke liye prompt taiyar karein
        prompt = f"""
        Create a 3D Cinematic Audio Drama Script based on the following details:
        Chapter: {chapter_no} - {chapter_title}
        System Name: {system_name}
        Dhruv Rank: {dhruv_rank}
        Concept / Storyline: {concept}
        """

        response = model.generate_content(prompt)
        return jsonify({'status': 'success', 'script': response.text})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
