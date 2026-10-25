import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API key from environment variable
# Make sure to set GEMINI_API_KEY in your Render Environment Variables
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

@app.route('/')
index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_script():
    try:
        data = request.get_json()
        concept = data.get('concept', '')
        
        if not concept:
            return jsonify({'error': 'Please enter an audio drama concept.'}), 400

        # Using the updated model name
        model_name = "models/gemini-1.5-flash"  # ya "gemini-3.8-flash" jo aapke account par active ho
        
        # Fallback or direct initialization
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )

        prompt = f"""
        Aap ek expert 3D Cinematic Audio Drama Writer hain. 
        Neeche diye gaye concept par ek engaging, high-energy aur cinematic audio drama script likhein, 
        isme sound effects cues (jaise [BG MUSIC: Intense Epic Beat], [SFX: Thunder]) bhi shamil hon:

        Concept: {concept}
        """

        response = model.generate_content(prompt)
        script_text = response.text

        return jsonify({'script': script_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
