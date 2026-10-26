import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# अपनी Gemini API Key यहाँ डालें या पर्यावरण चर (Environment Variable) का उपयोग करें
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/generate-script', methods=['POST'])
def generate_script():
    try:
        data = request.json
        user_prompt = data.get("prompt", "")

        if not user_prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # FIX: पुराना 'gemini-pro' मॉडल हटाकर नया समर्थित मॉडल 'gemini-1.5-flash' या 'gemini-1.5-pro' इस्तेमाल करें
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(user_prompt)

        return jsonify({"script": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
