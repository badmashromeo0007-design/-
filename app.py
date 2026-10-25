import os
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Configure Gemini API using the standard library compatible with google-generativeai==0.8.3
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

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
                <button onclick="copyOutput()" class="bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs px-
