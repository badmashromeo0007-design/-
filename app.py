import os
from flask import Flask, render_template, request
from google import genai

app = Flask(__name__)
client = genai.Client()

@app.route("/", methods=["GET", "POST"])
def index():
    generated_script = ""
    if request.method == "POST":
        story_input = request.form.get("story_input")
        
        prompt = f"""
        Aapko niche di gayi story/details ke adhar par ek engaging audio chapter script (Screenplay Format) taiyar karni hai:
        
        {story_input}
        
        Dialogue progression, character power dynamics aur scene ka tone bilkul natural aur professional hona chahiye.
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
  
