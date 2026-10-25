from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Aapki di gayi API key yahan add kar di gayi hai
GEMINI_API_KEY = "AQ.Ab8RN6IWgrb08CuMTHyr9SIzlGRj6U4H0SAAo2gBzfAcgSWBxA"

genai.configure(api_key=GEMINI_API_KEY)

# Updated Model Name
model = genai.GenerativeModel("models/gemini-3.8-flash")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-script', methods=['POST'])
def generate_script():
    try:
        data = request.get_json()
        concept = data.get('concept', '')
        chapter_no = data.get('chapter_no', '1')
        chapter_title = data.get('chapter_title', '')
        system_name = data.get('system_name', '')
        dhruv_rank = data.get('dhruv_rank', '')

        prompt = f"""
        Act as a professional 3D Cinematic Audio Drama Script Writer.
        Create a detailed Hindi script & prompts based on:
        - Chapter No: {chapter_no}
        - Chapter Title: {chapter_title}
        - Unique System Name: {system_name}
        - Dhruv Current Rank: {dhruv_rank}
        - Concept / Storyline: {concept}
        
        Write an engaging audio drama script in Hindi with cinematic scene descriptions and visual video prompts.
        """

        response = model.generate_content(prompt)
        return jsonify({'status': 'success', 'script': response.text})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
