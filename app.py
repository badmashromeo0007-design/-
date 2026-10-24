import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from google import genai

app = Flask(__name__)

# Initialize Google Gemini Client (fetches GEMINI_API_KEY from environment or explicit key)
# os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY_HERE"
client = genai.Client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_chapter', methods=['POST'])
def generate_chapter():
    data = request.json or {}
    
    story_summary = data.get('story_summary', '')
    chapter_number = data.get('chapter_number', 1)
    chapter_title = data.get('chapter_title', '')
    num_scenes = data.get('num_scenes', 5)
    
    # Advanced Character & Environment Metadata
    character_profiles = data.get('character_profiles', '')
    time_skip_info = data.get('time_skip_info', '')
    primary_location = data.get('primary_location', 'Mesoriodia City / Shorye Mahal')
    visual_style = data.get('visual_style', '3D Animated Cinematic (Unreal Engine 5)')

    if not story_summary.strip():
        return jsonify({'error': 'Story idea or chapter concept is required.'}), 400

    prompt = f"""
    You are a Lead 3D Animation Director, Senior Sound Designer, and Master Screenwriter for High-End Cinematic Animated Audio Dramas (similar to Super Yoddha).

    ======================================================================
    MASTER STORY & PRODUCTION CONTEXT
    ======================================================================
    - Core Concept / Outline: "{story_summary}"
    - Primary Location / Setting: {primary_location}
    - Time Skip / Timeline Context: {time_skip_info if time_skip_info else "Standard Timeline"}
    - Visual Aesthetic Style: {visual_style}

    CHARACTER BIBLE & PROGRESSION TRACKER:
    - Dhruv: Protagonist. Ages and evolves from a weak/mocked youth to a fierce 3D fantasy warrior. Uses magical ring and Amrit Dhara. Fists feature glowing aura energy and particle VFX during combat.
    - Lara Zayan: Rival / Former fiancee. Leader of Ambar Dal. Ambitious, sharp 3D visual design, authoritative voice tone.
    - Acharya Vidur / Guru: Mystic mentor residing in the spirit/ring realm.
    - Additional Supporting/Enemy Characters: {character_profiles if character_profiles else "Dynamic as introduced in the narrative."}

    ======================================================================
    PRODUCTION & GENERATION DIRECTIVES
    ======================================================================
    Generate a complete, highly detailed 3D Cinematic Script and Storyboard for:
    - Chapter Number: {chapter_number}
    - Chapter Title: {chapter_title if chapter_title else f'Chapter {chapter_number}'}
    - Target Scenes in Chapter: {num_scenes}

    STRICT GUIDELINES:
    1. 3D ANIMATION CINEMATIC VISUALS: All video and keyframe prompts MUST be tailored for Unreal Engine 5 render style, 3D high-poly stylized character models, cinematic volumetric lighting, raytracing reflections, and particle VFX (sparks, shockwaves, elemental auras).
    2. DYNAMIC MUSIC (BGM) & SFX ADAPTATION: Background music and sound effects MUST adapt dynamically as scene moods transition (e.g., tense suspense -> emotional heartbreak -> explosive high-octane 3D fight action).
    3. SCENE & LOCATION TRANSITIONS: Explicitly denote changes in scenery, time-skips, and character age/look adjustments.

    For EACH Scene (1 to {num_scenes}), generate the following EXACT structured sections:

    ======================================================================
    SCENE {chapter_number}.X: [Scene Title]
    ======================================================================
    [LOCATION & TIME]: e.g., Shorye Mahal / Graveyard (3 Years Later)
    [ACTIVE CHARACTERS & STATUS]: Names, current age/look, and power rank.
    [SCENE MOOD]: e.g., Suspense, Emotional Heartbreak, High-Octane 3D Battle.

    1. DYNAMIC AUDIO & MUSIC DESIGN (BGM & SFX):
       - BGM Cues: Specific instruments, tempo, and emotional mood shifts.
       - SFX Cues: Exact sound effects timed with character actions and magic usage.

    2. HINDI / HINGLISH DIALOGUE & NARRATION:
       - Full dramatic script with voice delivery tags (e.g., [Gusse me], [Dheere se], [Chillakar]).

    3. 3D ANIMATION VIDEO PROMPT (Sora / Runway Gen-3 / Luma Dream Machine):
       - Detailed English prompt: 3D animated style, Unreal Engine 5 render, camera movement (close-up, tracking, low-angle hero shot), lighting, particle VFX, slow-motion impact beats, 4K resolution.

    4. KEYFRAME IMAGE PROMPT (Midjourney v6 / Leonardo AI):
       - Cinematic 3D keyframe prompt for thumbnail and storyboard visual references.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return jsonify({
            'success': True,
            'result': response.text,
            'chapter_number': chapter_number,
            'chapter_title': chapter_title
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
