import os
from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# API Key configure karein
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    generated_script = ""
    if request.method == "POST":
        story_input = request.form.get("story_input")
        
        prompt = f"""
        Aap ek expert cinematic anime scriptwriter hain. Niche di gayi story ke adhar par ek ultra-realistic aur high-level audio/video screenplay script taiyar karni hai. 
        Vibe, characters aur tone bilkul 'Battle Through The Heavens' (斗破苍穹) universe ke original characters (jaise Xiao Yan, Yao Lao, Xun Er, Medusa) ke hisab se honi chahiye.

        ULTRA-REALISTIC CHARACTER & CINEMATIC RULEBOOK:
        1. **Strict BTTH Characters Only:** Story mein sirf 'Battle Through The Heavens' ke established characters aur unke power systems (Qi methods, Flame attributes) ka use ho.
        2. **Hyper-Realistic Character Depth:** Characters artificial ya robotic nahi lagne chahiye. Unka reaction, ankhon ke bhav, saansein chalna, aura ka tharthrana, aur darr ya gussa bilkul real-life human emotions aur high-end cinematic standards ke mutabiq likha ho.
        3. **Real Visual & Audio Experience (VFX/SFX):** Video bilkul real aur heavy-impact lagni chahiye. Har scene ke sath brackets mein clear visual aur sound cues likhein:
           - [Visual: Realistic sweat dropping, micro-expressions, space distortion, ground shattering under pressure, intense soul aura glowing]
           - [SFX: Heavy bass thunder, realistic footsteps, high-frequency energy hum, sharp weapon clashing sound]
           - [System / Mentor Alert]: Yao Lao ki telepathic voice ya system alert jo Dhruv aur audience ko samne wale ki power rank turant bataye.
        4. **Cinematic BGM:** Har fight aur emotional moment par heavy orchestral aur suspenseful background music ka transition ho.

        Story Input / Raw Context:
        {story_input}
        """
        
        try:
            # Sabse stable aur tested model
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            generated_script = response.text
        except Exception as e:
            generated_script = f"Error generating script: {str(e)}"
            
    return render_template("index.html", generated_script=generated_script)

if __name__ == "__main__":
    app.run(debug=True)
    
