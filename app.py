from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

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
        char1_name = data.get('char1_name', '')
        char1_rank = data.get('char1_rank', '')
        char2_name = data.get('char2_name', '')
        char2_rank = data.get('char2_rank', '')

        prompt = f"""
        Act as a professional 3D Cinematic Audio Drama Script Writer.
        Create a detailed Hindi script & dialogue prompts based on:
        - Chapter No: {chapter_no}
        - Chapter Title: {chapter_title}
        - Unique System Name: {system_name}
        - Character 1: {char1_name} (Rank: {char1_rank})
        - Character 2: {char2_name} (Rank: {char2_rank})
        - Concept / Storyline: {concept}

        Write an engaging audio drama script in Hindi including character names, individual ranks, cinematic scene descriptions, and visual video prompts.
        """

        response = model.generate_content(prompt)
        script_text = response.text

        return jsonify({'status': 'success', 'script': script_text})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
