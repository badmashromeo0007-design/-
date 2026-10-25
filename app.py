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
        Aap ek expert cinematic anime scriptwriter hain. Niche di gayi story/details ke adhar par ek high-level audio/video screenplay script taiyar karni hai. 
        Vibe aur tone bilkul 'Battle Through The Heavens' (斗破苍穹) jaisa high-fantasy aur xianxia style hona chahiye.

        AUTOMATIC CHARACTER & DYNAMIC POWER RULEBOOK:
        1. **Auto Character Extraction & Introduction:** Story ke text ko analyze karke khud-ba-khud 'Battle Through The Heavens' universe ke matching characters (jaise Xiao Yan, Yao Lao, Xun Er, Medusa ya story ke naye characters) ko detect karein aur unke roles ko script mein dynamically shamil karein. Jaise-jaise story aage badhe, naye characters automatically introduce hone chahiye.
        2. **Dynamic Power Ranks & Aura Control:** Characters ki powers aur aura pressure ko story ke sequence ke hisab se scale up/down karein. Agar koi powerful entity aas-paas ke area ko control karti hai, toh uska impact saaf dikhe.
        3. **Audience Clarity (VFX, SFX & System Alerts):** Audience ko power levels aur darr samajhne ke liye har scene mein bracket `[ ]` mein clear cues likhein:
           - [Visual: Aura pressure shaking the ground / Space distortion]
           - [SFX: Heavy thunder bass / High energy hum]
           - [System / Mentor Alert]: Yao Lao ya system voice ki tarah telepathic warning ho jo Dhruv aur audience ko samne wale ki power rank turant bataye.
        4. **Cinematic BGM:** Har mood aur fight ke hisab se background music transitions mention karein.

        Story Input / Raw Context:
        {story_input}
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
    
