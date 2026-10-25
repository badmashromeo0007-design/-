import os
import time
import asyncio
import edge_tts
import requests
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3.8-flash')

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

# Ensure audio directory exists
AUDIO_DIR = os.path.join(os.getcwd(), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    summary = data.get('story_summary', '')
    ch_num = data.get('chapter_number', '1')
    ch_title = data.get('chapter_title', 'Chapter')
    scenes = data.get('num_scenes', '5')
    dhruv_rank = data.get('dhruv_rank', '3rd Star (Shunya Rank)')
    system_name = data.get('system_name', 'DIVINE SOUL SYSTEM')

    prompt = f"""
    You are an expert Lead 3D Animation Director, Master Sound Designer, and Screenwriter combining the powerful progression style of 'Battle Through The Heavens' with the 'Super Yoddha' universe.

    UNIQUE SYSTEM INTEGRATION:
    - Active System Name: [{system_name}]
    - Every time Dhruv faces a crisis, a breakthrough, or a powerful opponent, the [{system_name}] must trigger a holographic digital notification box in the script detailing his status, rewards, power gaps, or warning alerts.

    FUSION CHARACTERS & WORLD CONTEXT:
    - Dhruv (Protagonist): Current Rank: {dhruv_rank}, linked with [{system_name}] and holding a secret ring mentor (Acharya Vidur).
    - Lara Zayan: Proud Ambar Dal leader, High Rank Warrior.
    - Acharya Vidur / Yao Lao: Spiritual mentor inside the ring.

    STRICT CINEMATIC & SYSTEM RULES:
    1. CHARACTER NAME & RANK TAG: Explicitly define on-screen visual intro tags ([TEXT OVERLAY: DHRUV | Rank: 3rd Star Shunya]).
    2. SYSTEM NOTIFICATION POP-UPS: Include glowing system status boxes in dialogues/scenes (e.g., [SYSTEM ALERT: Energy fluctuation detected! Enemy Rank: Dou Wang. Survival Probability: 12%]).
    3. ISOLATED / SOLO SCENE EXPOSITION: Use environmental pressure, system warnings, and inner monologues.

    Task:
    Generate a detailed 3D Cinematic Animation Script, Subtitles (.SRT format cues), and Storyboard with [{system_name}] logs for Chapter {ch_num}: {ch_title} ({scenes} scenes).

    STRICT FORMAT FOR EACH SCENE (1 to {scenes}):
    - SCENE HEADER & LOCATION
    - ACTIVE CHARACTERS & ON-SCREEN NAME/RANK TAGS
    - [{system_name}] NOTIFICATION LOGS & POWER EXPOSITION
    - DYNAMIC CINEMATIC BGM & SFX CUES
    - HINDI / HINGLISH VOICE-OVER & DIALOGUES (With delivery tags)
    - 3D ANIMATION VIDEO PROMPT (English prompt for Sora/Runway/Luma specifying Unreal Engine 5 style, volumetric lighting, particle aura)
    
    Story Input: {summary}
    """

    try:
        response = model.generate_content(prompt)
        return jsonify({'success': True, 'result': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    """Generates Hindi Voiceover MP3 using Edge TTS"""
    data = request.json or {}
    text = data.get('text', '')
    voice_type = data.get('voice_type', 'hi-IN-MadhurNeural') # Madhur (Male) or Swara (Female)

    if not text.strip():
        return jsonify({'success': False, 'error': 'Voiceover text khali hai!'}), 400

    filename = f"voice_{int(time.time())}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    async def _save_audio():
        communicate = edge_tts.Communicate(text, voice_type)
        await communicate.save(filepath)

    try:
        asyncio.run(_save_audio())
        return jsonify({'success': True, 'audio_url': f"/static/audio/{filename}"})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.json or {}
    prompt_text = data.get('prompt', '')

    if not REPLICATE_API_TOKEN:
        return jsonify({'success': False, 'error': 'REPLICATE_API_TOKEN is not set.'}), 400

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "luma/ray",
        "input": {
            "prompt": f"3D Unreal Engine 5 cinematic animation style, high quality, 4k, dark fantasy, dynamic camera movement, {prompt_text}",
            "aspect_ratio": "16:9"
        }
    }

    try:
        res = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        res_data = res.json()
        
        if "id" in res_data:
            prediction_id = res_data["id"]
            for _ in range(30):
                time.sleep(3)
                check_res = requests.get(f"https://api.replicate.com/v1/predictions/{prediction_id}", headers=headers)
                check_data = check_res.json()
                if check_data.get("status") == "succeeded":
                    return jsonify({'success': True, 'video_url': check_data['output']})
                elif check_data.get("status") == "failed":
                    return jsonify({'success': False, 'error': 'Video generation failed.'})

        return jsonify({'success': False, 'error': 'Video generation timed out.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
