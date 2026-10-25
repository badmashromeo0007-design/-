import os
import time
import asyncio
import edge_tts
import requests
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_from_directory
from moviepy.editor import VideoFileClip, AudioFileClip

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
    You are an expert Lead 3D Animation Director, Master Sound Designer, and Screenwriter combining progression style of 'Battle Through The Heavens' with 'Super Yoddha'.
    Active System: [{system_name}], Dhruv Rank: {dhruv_rank}.
    Generate detailed 3D Cinematic Script with [{system_name}] logs for Chapter {ch_num}: {ch_title} ({scenes} scenes) including character voice lines and Unreal Engine 5 video prompts.
    Story Input: {summary}
    """
    try:
        response = model.generate_content(prompt)
        return jsonify({'success': True, 'result': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
                    return jsonify({'success': False, 'error': 'Video failed.'})

        return jsonify({'success': False, 'error': 'Timeout.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/merge-media', methods=['POST'])
def merge_media():
    """Auto-merges rendered 3D video URL and generated Audio MP3 file into one final video"""
    data = request.json or {}
    video_url = data.get('video_url', '')
    audio_path_relative = data.get('audio_path', '')

    if not video_url or not audio_path_relative:
        return jsonify({'success': False, 'error': 'Video URL ya Audio path missing hai!'}), 400

    try:
        # Download remote video locally temporarily
        vid_res = requests.get(video_url)
        temp_vid_path = os.path.join(VIDEO_DIR, f"temp_vid_{int(time.time())}.mp4")
        with open(temp_vid_path, 'wb') as f:
            f.write(vid_res.content)

        # Full path for audio
        full_audio_path = os.path.join(os.getcwd(), audio_path_relative.lstrip('/'))
        output_filename = f"final_scene_{int(time.time())}.mp4"
        output_filepath = os.path.join(VIDEO_DIR, output_filename)

        # MoviePy combining video and audio
        video_clip = VideoFileClip(temp_vid_path)
        audio_clip = AudioFileClip(full_audio_path)

        # Match durations seamlessly
        if audio_clip.duration > video_clip.duration:
            # Loop or extend video slightly if audio is longer, or trim audio
            audio_clip = audio_clip.subclipped(0, video_clip.duration)
        
        final_clip = video_clip.with_audio(audio_clip)
        final_clip.write_videofile(output_filepath, codec='libx264', audio_codec='aac', fps=24, logger=None)

        # Close clips
        video_clip.close()
        audio_clip.close()
        final_clip.close()

        # Remove temp source
        if os.path.exists(temp_vid_path):
            os.remove(temp_vid_path)

        return jsonify({'success': True, 'final_video_url': f"/static/video/{output_filename}"})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
