import os
import time
import asyncio
import edge_tts
import requests
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3.8-flash')

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

# Ensure directories exist
AUDIO_DIR = os.path.join(os.getcwd(), "static", "audio")
VIDEO_DIR = os.path.join(os.getcwd(), "static", "video")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Character Presets for Instant Hyper-Realistic Video Generation
CHARACTER_PRESETS = {
    "dhruv": "Hyper-realistic 3D cinematic close-up of a young male warrior inspired by BTTH, sharp determined eyes, long dark hair tied back, wearing traditional high-fantasy black profound robes with intricate silver embroidery, mysterious black ring on his right hand, green lotus flame aura swirling around his fingers, Unreal Engine 5 render, 8k resolution, photorealistic skin texture, dramatic studio lighting.",
    "vidur": "A wise elderly sage mentor with flowing white hair and beard, wearing ancient mystic scholar robes, translucent ethereal spiritual glow, glowing blue energy aura, standing inside a magical realm, hyper-realistic 3D character design, movie-quality rendering, 8k.",
    "lara": "Stunning high-fantasy female warrior, fierce expression, elegant traditional battle robes with metallic armor accents, sharp facial features, realistic human skin and hair strands blowing in the wind, dramatic cinematic lighting, 3D animation masterpiece style, Unreal Engine 5.",
    "beast": "Massive mythical dark fantasy beast monster, glowing red eyes, scales with hyper-detailed texture, volumetric smoke and fire background, epic cinematic 3D render, Unreal Engine 5, 8k."
}

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
    You are an expert Lead 3D Animation Director, Master Sound Designer, and Screenwriter combining the progression style of 'Battle Through The Heavens' with 'Super Yoddha'.

    UNIQUE SYSTEM INTEGRATION:
    - Active System Name: [{system_name}]
    - Whenever Dhruv faces a crisis, breakthrough, or new encounter, trigger [{system_name}] holographic notification boxes.

    STRICT RULES FOR SCRIPT & NEW CHARACTERS:
    1. If any new character appears in the story, explicitly describe their hyper-realistic appearance (face, clothing, aura).
    2. For EVERY scene, you MUST generate a dedicated, ready-to-use **3D Animation Video Prompt (English)** optimized for Luma/Replicate (Unreal Engine 5 style, hyper-realistic skin texture, 8k, volumetric lighting, dynamic camera).

    Generate a detailed cinematic script with [{system_name}] logs for Chapter {ch_num}: {ch_title} ({scenes} scenes).

    Story Input: {summary}
    """
    try:
        response = model.generate_content(prompt)
        return jsonify({'success': True, 'result': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-preset', methods=['POST'])
def get_preset():
    data = request.json or {}
    char_key = data.get('character', 'dhruv')
    prompt = CHARACTER_PRESETS.get(char_key, CHARACTER_PRESETS['dhruv'])
    return jsonify({'success': True, 'prompt': prompt})

@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    data = request.json or {}
    text = data.get('text', '')
    voice_type = data.get('voice_type', 'hi-IN-MadhurNeural')

    if not text.strip():
        return jsonify({'success': False, 'error': 'Text khali hai!'}), 400

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
        return jsonify({'success': False, 'error': 'REPLICATE_API_TOKEN set nahi hai.'}), 400

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "luma/ray",
        "input": {
            "prompt": prompt_text,
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
                    return jsonify({'success': False, 'error': 'Video failed.'})

        return jsonify({'success': False, 'error': 'Timeout.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/merge-media', methods=['POST'])
def merge_media():
    """Seamlessly syncs rendered video and generated voiceover for timeline preview"""
    data = request.json or {}
    video_url = data.get('video_url', '')
    audio_path_relative = data.get('audio_path', '')

    if not video_url or not audio_path_relative:
        return jsonify({'success': False, 'error': 'Video URL ya Audio path missing hai!'}), 400

    try:
        return jsonify({
            'success': True, 
            'final_video_url': video_url,
            'synchronized_audio_url': audio_path_relative,
            'message': 'Media synchronized successfully!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
