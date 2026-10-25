import os
from flask import Flask, render_template, request
from google import genai

app = Flask(__name__)
client = genai.Client()

@app.route("/", methods=["GET", "POST"])
def index():
    generated_script = ""
    if request.method == "POST":
        chapter_title = request.form.get("chapter_title")
        system_name = request.form.get("system_name")
        char1_name = request.form.get("char1_name")
        char1_rank = request.form.get("char1_rank")
        char2_name = request.form.get("char2_name")
        char2_rank = request.form.get("char2_rank")
        story_context = request.form.get("story_context")
        
        prompt = f"""
        Create an engaging audio chapter script based on the following details:
        - Chapter Title: {chapter_title}
        - System Name: {system_name}
        - Character 1: {char1_name} (Current Rank: {char1_rank})
        - Character 2: {char2_name} (Current Rank: {char2_rank})
        - Story Details/Context: {story_context}
        
        Reflect the current rank, power dynamics, and story context accurately in the dialogues and scene progression.
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
            )
            generated_script = response.text
        except Exception as e:
            generated_script = f"Error generating script: {str(e)}"
            
    return render_template("index.html", generated_script=generated_script)

if __name__ == "__main__":
    app.run(debug=True)
