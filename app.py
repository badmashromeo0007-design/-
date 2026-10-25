import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Aapki Gemini API Key yahan set karein ya environment variable se lein
# os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"
client = genai.Client() if 'genai' in globals() else None

# Agar google-genai import karna ho:
from google import genai
client = genai.Client()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Cinematic Audio Drama Studio - BTTH x Super Yoddha</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #08080c; color: #f3f4f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .red-glow { border: 1px solid rgba(220, 38, 38, 0.4); box-shadow: 0 0 30px rgba(220, 38, 38, 0.15); }
        .custom-scrollbar::-webkit-scrollbar { width: 8px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #0f0f15; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #374151; border-radius: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ef4444; }
    </style>
</head>
<body class="min-h-screen py-8 px-4 custom-scrollbar">
    <div class="max-w-5xl mx-auto">
        <!-- Header -->
        <header class="text-center mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-red-600 tracking-wider">CINEMATIC 3D AUDIO DRAMA STUDIO</h1>
            <p class="text-gray-400 text-xs md:text-sm mt-2">Battle Through The Heavens × Super Yoddha Fusion Generator</p>
        </header>

        <!-- Control Panel -->
        <div class="red-glow bg-gray-900/90 rounded-2xl p-6 md:p-8 backdrop-blur-md mb-8">
            <div class="mb-5">
                <label class="block text-sm font-bold text-amber-400 mb-2">Episode Concept / Next Storyline *</label>
                <textarea id="story_summary" rows="4" class="w-full bg-black/80 border border-gray-700 rounded-xl p-3.5 text-white focus:outline-none focus:border-red-500 text-sm" placeholder="Example: Episode 2 - Dhruv ka 3 saal ka safar aur training. Angoothi ke andar se Acharya Vidur ka milna, aur Ambar Dal ki leader Lara Zayan ke khilaf taiyari shuru karna..."></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1.5">Episode / Chapter No.</label>
                    <input type="number" id="chapter_number" value="2" class="w-full bg-black/80 border border-gray-700 rounded-lg p-3 text-white text-sm">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1.5">Episode Title</label>
                    <input type="text" id="chapter_title" value="Episode 2: Aakhri Shart aur Nayi Taqat" class="w-full bg-black/80 border border-gray-700 rounded-lg p-3 text-white text-sm">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1.5">Scenes Count</label>
                    <select id="num_scenes" class="w-full bg-black/80 border border-gray-700 rounded-lg p-3 text-white text-sm">
                        <option value="3">3 Scenes</option>
                        <option value="5" selected>5 Scenes</option>
                        <option value="8">8 Scenes</option>
                    </select>
                </div>
            </div>

            <button onclick="generateScript()" id="genBtn" class="w-full bg-red-600 hover:bg-red-700 text-white font-extrabold py-3.5 px-6 rounded-xl transition tracking-wide shadow-lg shadow-red-950/80 text-sm md:text-base">
                GENERATE 3D CINEMATIC SCRIPT & PROMPTS 🎬✨
            </button>
        </div>

        <!-- Output Section -->
        <div id="outputSection" class="hidden red-glow bg-gray-900/90 rounded-2xl p-6 md:p-8 backdrop-blur-md">
            <div class="flex justify-between items-center mb-4 border-b border-gray-800 pb-3">
                <h2 class="text-lg md:text-xl font-bold text-amber-400">Cinematic Script & Audio/Visual Storyboard</h2>
                <button onclick="copyOutput()" class="bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs px-3 py-1.5 rounded border border-gray-600">Copy Script 📋</button>
            </div>
            <div id="resultContent" class="pl-4 border-l-4 border-red-500 whitespace-pre-wrap text-gray-200 leading-relaxed font-mono text-xs md:text-sm"></div>
        </div>
    </div>

    <script>
        async function generateScript() {
            const story_summary = document.getElementById('story_summary').value;
            const chapter_number = document.getElementById('chapter_number').value;
            const chapter_title = document.getElementById('chapter_title').value;
            const num_scenes = document.getElementById('num_scenes').value;
            const btn = document.getElementById('genBtn');
            const outputSection = document.getElementById('outputSection');
            const resultContent = document.getElementById('resultContent');

            if (!story_summary.trim()) {
                alert('Kripya episode ka concept ya summary daalein!');
                return;
            }

            btn.disabled = true;
            btn.innerText = 'Creating 3D Script & Cinematic Music Cues...';
            outputSection.classList.add('hidden');

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ story_summary, chapter_number, chapter_title, num_scenes })
                });

                const data = await response.json();
                if (data.success) {
                    resultContent.innerText = data.result;
                    outputSection.classList.remove('hidden');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (err) {
                alert('Kuch galat ho gaya! Check connection.');
                console.error(err);
            } finally {
                btn.disabled = false;
                btn.innerText = 'GENERATE 3D CINEMATIC SCRIPT & PROMPTS 🎬✨';
            }
        }

        function copyOutput() {
            navigator.clipboard.writeText(document.getElementById('resultContent').innerText);
            alert('Script copied to clipboard!');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    summary = data.get('story_summary', '')
    ch_num = data.get('chapter_number', '1')
    ch_title = data.get('chapter_title', 'Chapter')
    scenes = data.get('num_scenes', '5')

    prompt = f"""
    You are an expert Lead 3D Animation Director, Master Sound Designer, and Screenwriter combining the powerful progression style of 'Battle Through The Heavens' (Doupo Cangqiong) with the 'Super Yoddha' universe script.

    FUSION CHARACTERS & WORLD CONTEXT:
    - Dhruv (Protagonist / Xiao Yan vibe): Currently humiliated, stuck at 3rd Star (Shunya Rank), but harbors a secret ring mentor and immense hidden potential.
    - Lara Zayan (Nalan Yanran / Queen Medusa vibe): Proud Ambar Dal leader who broke her engagement and challenged Dhruv with a 3-year ultimatum.
    - Arendra: Supportive father and Shorye Dal leader.
    - Ira: Loyal childhood friend (Xun Er vibe).
    - Acharya Vidur / Yao Lao: Mysterious spiritual mentor residing in the ring.

    Task:
    Generate a detailed 3D Cinematic Animation Script and Storyboard for Chapter {ch_num}: {ch_title} ({scenes} scenes).

    STRICT GUIDELINES:
    1. 3D ANIMATION VISUALS: Unreal Engine 5 render style, high-poly stylized characters with rich Indian/Eastern fantasy features, volumetric cinematic lighting, raytracing, and particle VFX (glowing flames, energy auras).
    2. CINEMATIC INDIAN-FUSION BGM & SFX: Background music must blend traditional Indian classical notes (sitar/bansuri) with heavy Hans Zimmer-style orchestral battle beats, changing dynamically with scene moods.
    3. NARRATIVE FLOW: Dramatic dialogues, intense emotions, and smooth location transitions.

    For EACH Scene (1 to {scenes}), provide:
    - SCENE HEADER & LOCATION
    - ACTIVE CHARACTERS & EMOTION/MOOD
    - DYNAMIC CINEMATIC BGM & SFX CUES (Detailed music progression)
    - HINDI / HINGLISH VOICE-OVER & DIALOGUES (With delivery tags)
    - 3D ANIMATION VIDEO PROMPT (English prompt for Sora/Runway specifying 3D cinematic style, camera angles, lighting, and VFX)
    
    Story Input: {summary}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return jsonify({'success': True, 'result': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
