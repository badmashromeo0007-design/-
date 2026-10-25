from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Render ke environment variable se key automatically uthegi
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional 3D Cinematic Audio Drama Script Writer."},
                {"role": "user", "content": prompt}
            ]
        )
        
        script_text = response.choices[0].message.content
        return jsonify({'status': 'success', 'script': script_text})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
