import os
import re
import uuid
import asyncio
import secrets
import logging
import sqlite3
from pathlib import Path
from contextlib import contextmanager

import edge_tts
from flask import (
    Flask, render_template, request, session,
    send_from_directory, abort, url_for
)
from groq import Groq
from werkzeug.utils import secure_filename

from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ColorClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR_VALUE = os.environ.get("DATA_DIR", "").strip()
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

if not DATA_DIR_VALUE:
    raise RuntimeError("Set DATA_DIR, for example /var/data.")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "Set FLASK_SECRET_KEY to a strong random secret of at least 32 characters."
    )

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is required.")

DATA_DIR = Path(DATA_DIR_VALUE).resolve()
STATIC_DIR = DATA_DIR / "static"
DB_PATH = DATA_DIR / "scripts.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=None)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    MAX_CONTENT_LENGTH=1024 * 1024,  # Maximum request body: 1 MB
    MAX_FORM_MEMORY_SIZE=256 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=(
        os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"
    ),
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
app.logger.setLevel(logging.INFO)

client = Groq(api_key=GROQ_API_KEY, timeout=60.0, max_retries=1)

MAX_STORY_LENGTH = 10_000
MAX_SCRIPT_LENGTH = 20_000
MAX_DIALOGUES = 100

VIDEO_PATTERN = re.compile(
    r"^video_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\.mp4$"
)

# --------------------------------------------------
# Database
# --------------------------------------------------

@contextmanager
def db_connection():
    conn = sqlite3.connect(str(DB_PATH), timeout=15)
    try:
        conn.execute("PRAGMA busy_timeout = 15000")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with db_connection() as conn:
        # Added session_id column for basic user script isolation
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                title TEXT NOT NULL,
                script_content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_vault_session
            ON vault(session_id, id DESC)
        """)

init_db()

def get_user_session_id():
    if "user_session_id" not in session:
        session["user_session_id"] = secrets.token_hex(16)
    return session["user_session_id"]

def get_saved_scripts():
    sess_id = get_user_session_id()
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT id, title, script_content
            FROM vault
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT 10
        """, (sess_id,)).fetchall()

    return [
        {"id": row[0], "title": row[1], "content": row[2]}
        for row in rows
    ]

# --------------------------------------------------
# CSRF protection
# --------------------------------------------------

@app.context_processor
def inject_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return {"csrf_token": session["csrf_token"]}

def valid_csrf():
    submitted = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")

    return bool(
        submitted
        and expected
        and secrets.compare_digest(submitted, expected)
    )

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def get_video_path(filename):
    safe_name = secure_filename(filename or "")

    if not safe_name or not VIDEO_PATTERN.fullmatch(safe_name):
        abort(404)

    path = STATIC_DIR / safe_name

    if not path.is_file():
        abort(404)

    return safe_name

def parse_script_into_scenes(script_text):
    scenes = []
    current_scene = {
        "title": "Scene 1",
        "visual": "Atmospheric cinematic opening",
        "dialogues": []
    }

    for raw_line in script_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.upper().startswith(("[SCENE", "SCENE")):
            if current_scene["dialogues"]:
                scenes.append(current_scene)
                current_scene = {
                    "title": line,
                    "visual": "Cinematic transition view",
                    "dialogues": []
                }
            else:
                current_scene["title"] = line
            continue

        if line.upper().startswith("VISUAL:"):
            current_scene["visual"] = line.split(":", 1)[1].strip()
            continue

        if ":" in line:
            parts = line.split(":", 1)
            character = parts[0].strip().strip("*_ ").lower()
            dialogue = parts[1].strip().strip("*_ ").strip()

            if not character or not dialogue:
                continue

            if character.startswith(("scene ", "episode ", "chapter ")):
                continue

            if "narrator" in character:
                voice = os.environ.get("NARRATOR_VOICE", "hi-IN-MadhurNeural")
            elif any(name in character for name in (
                "xun er", "xun'er", "medusa", "queen",
                "cai lin", "qingshan"
            )):
                voice = os.environ.get("FEMALE_VOICE", "hi-IN-SwaraNeural")
            else:
                voice = os.environ.get("MALE_VOICE", "hi-IN-MadhurNeural")

            current_scene["dialogues"].append((dialogue, voice))

            if sum(len(s["dialogues"]) for s in scenes) + len(current_scene["dialogues"]) >= MAX_DIALOGUES:
                break

    if current_scene["dialogues"]:
        scenes.append(current_scene)

    if not scenes:
        all_dialogues = []
        for raw_line in script_text.splitlines():
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            parts = line.split(":", 1)
            character = parts[0].strip().strip("*_ ").lower()
            dialogue = parts[1].strip().strip("*_ ").strip()
            if not character or not dialogue:
                continue
            if "narrator" in character:
                voice = os.environ.get("NARRATOR_VOICE", "hi-IN-MadhurNeural")
            elif any(name in character for name in ("xun er", "xun'er", "medusa", "queen", "cai lin", "qingshan")):
                voice = os.environ.get("FEMALE_VOICE", "hi-IN-SwaraNeural")
            else:
                voice = os.environ.get("MALE_VOICE", "hi-IN-MadhurNeural")
            all_dialogues.append((dialogue, voice))

        chunk_size = 4
        for i in range(0, max(1, len(all_dialogues)), chunk_size):
            chunk = all_dialogues[i:i+chunk_size]
            if chunk:
                scenes.append({
                    "title": f"Scene {(i//chunk_size)+1}",
                    "visual": "Cinematic sequence",
                    "dialogues": chunk
                })

    return scenes

def get_mood_color_from_visual(visual_text):
    vt = visual_text.lower()
    if any(w in vt for w in ["fire", "crimson", "red", "anger", "blood", "flame", "battle", "fight"]):
        return (42, 18, 24)   # Deep Crimson
    elif any(w in vt for w in ["forest", "emerald", "green", "nature", "tree", "plant", "calm"]):
        return (18, 40, 30)   # Dark Emerald
    elif any(w in vt for w in ["night", "dark", "shadow", "navy", "deep", "mystic", "cave", "nightfall"]):
        return (18, 32, 45)   # Midnight Navy
    elif any(w in vt for w in ["purple", "royal", "energy", "aura", "spirit", "breakthrough", "pill"]):
        return (38, 24, 45)   # Royal Purple
    else:
        return (24, 28, 36)   # Default Charcoal/Slate

async def create_audio_files(dialogues_to_generate, output_paths):
    semaphore = asyncio.Semaphore(3)

    async def generate_one(dialogue, voice, path):
        async with semaphore:
            communicate = edge_tts.Communicate(dialogue, voice)
            await communicate.save(str(path))

    tasks = [
        generate_one(item[0], item[1], path)
        for item, path in zip(dialogues_to_generate, output_paths)
    ]
    await asyncio.gather(*tasks)

def close_quietly(resource):
    if resource is not None:
        try:
            resource.close()
        except Exception:
            app.logger.warning(
                "A media resource could not be closed cleanly.",
                exc_info=True,
            )

def render_page(
    generated_script="",
    current_script_id=None,
    video_filename="",
    video_ready=False,
    error_message="",
    story_input="",
):
    try:
        saved_scripts = get_saved_scripts()
    except Exception:
        app.logger.exception("Could not load Script Vault.")
        saved_scripts = []
        if not error_message:
            error_message = "Script Vault is temporarily unavailable."

    return render_template(
        "index.html",
        generated_script=generated_script,
        current_script_id=current_script_id,
        video_filename=video_filename,
        video_ready=video_ready,
        error_message=error_message,
        story_input=story_input,
        saved_scripts=saved_scripts,
    )

# --------------------------------------------------
# Error handlers
# --------------------------------------------------

@app.errorhandler(413)
def request_too_large(_error):
    return render_page(
        error_message="Request too large. Please shorten your story or script."
    ), 413

@app.errorhandler(404)
def not_found(_error):
    return "Not found", 404

# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/health")
def health():
    return "OK", 200

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_page()

    if not valid_csrf():
        return render_page(
            error_message="Your form session expired. Refresh the page and try again."
        ), 400

    action = request.form.get("action", "").strip()
    story_input = request.form.get("story_input", "").strip()
    sess_id = get_user_session_id()

    if action == "generate_script":
        if not story_input:
            return render_page(
                error_message="Please enter a story.",
                story_input=story_input,
            ), 400

        if len(story_input) > MAX_STORY_LENGTH:
            return render_page(
                error_message="Story limit is 10,000 characters.",
                story_input=story_input[:MAX_STORY_LENGTH],
            ), 400

        prompt = f"""
You are a cinematic anime screenplay writer for 'Battle Through The Heavens' (斗破苍穹).
Write a clear Hindi/Hinglish screenplay based on the user's story.
Preserve emotional tone and character depth.
Structure the script into distinct scenes. Start each scene with `[SCENE N: Title]` followed by `VISUAL: [Scene description/mood]`.
Format spoken dialogue as `Character Name: dialogue`. Use `Narrator:` for narration.

Story:
{story_input}
"""

        try:
            model_name = os.environ.get(
                "GROQ_MODEL", "llama-3.3-70b-versatile"
            )

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )

            generated_script = (
                response.choices[0].message.content or ""
            ).strip()

            if not generated_script:
                raise ValueError("The model returned an empty script.")

            title = story_input.splitlines()[0][:80]

            with db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO vault (session_id, title, script_content)
                    VALUES (?, ?, ?)
                    """,
                    (sess_id, title or "Cinematic Script", generated_script),
                )
                current_script_id = cursor.lastrowid

            return render_page(
                generated_script=generated_script,
                current_script_id=current_script_id,
                story_input=story_input,
            )

        except Exception:
            app.logger.exception("Script generation failed.")
            return render_page(
                error_message=(
                    "Script generation failed. Please try again later."
                ),
                story_input=story_input,
            ), 500

    if action == "generate_video":
        script_id_raw = request.form.get("script_id", "").strip()

        if not script_id_raw.isdigit():
            return render_page(
                error_message="Invalid script reference."
            ), 400

        script_id = int(script_id_raw)

        # Secure Ownership Check: Fetch script only if it matches current session_id
        try:
            with db_connection() as conn:
                row = conn.execute(
                    "SELECT script_content FROM vault WHERE id = ? AND session_id = ?",
                    (script_id, sess_id),
                ).fetchone()
        except Exception:
            app.logger.exception("Database query failed while fetching script for video.")
            row = None

        if not row:
            return render_page(
                error_message="Script not found or unauthorized access."
            ), 400

        script_text = row[0]

        if len(script_text) > MAX_SCRIPT_LENGTH:
            return render_page(
                generated_script=script_text,
                current_script_id=script_id,
                error_message="Script limit is 20,000 characters.",
            ), 400

        scenes = parse_script_into_scenes(script_text)

        if not scenes or not any(s["dialogues"] for s in scenes):
            return render_page(
                generated_script=script_text,
                current_script_id=script_id,
                error_message=(
                    "No valid dialogues found. Ensure format is 'Character: Dialogue'."
                ),
            ), 400

        job_id = uuid.uuid4()
        temp_files = []
        scene_video_clips = []
        scene_audio_clips_list = []
        final_video = None
        output_path = None
        video_filename = ""

        try:
            flat_dialogues = []
            dialogue_mapping = []

            for s_idx, scene in enumerate(scenes):
                for d_idx, (dialogue, voice) in enumerate(scene["dialogues"]):
                    flat_dialogues.append((dialogue, voice))
                    dialogue_mapping.append((s_idx, d_idx))

            audio_paths = []
            for index in range(len(flat_dialogues)):
                path = DATA_DIR / f"temp_{job_id}_{index}.mp3"
                temp_files.append(path)
                audio_paths.append(path)

            asyncio.run(create_audio_files(flat_dialogues, audio_paths))

            scene_audio_clips = {i: [] for i in range(len(scenes))}
            for mapping_idx, path in enumerate(audio_paths):
                if not path.is_file() or path.stat().st_size == 0:
                    raise RuntimeError(f"Audio segment {mapping_idx} was not created.")
                s_idx, _ = dialogue_mapping[mapping_idx]
                aclip = AudioFileClip(str(path))
                scene_audio_clips[s_idx].append(aclip)
                scene_audio_clips_list.append(aclip)

            for s_idx, scene in enumerate(scenes):
                s_audios = scene_audio_clips.get(s_idx, [])
                if not s_audios:
                    continue

                scene_audio = concatenate_audioclips(s_audios)
                scene_audio_clips_list.append(scene_audio)
                scene_duration = scene_audio.duration

                visual_desc = scene.get("visual", "")
                color = get_mood_color_from_visual(visual_desc)

                vclip = ColorClip(size=(1280, 720), color=color).with_duration(scene_duration)
                scene_video = vclip.with_audio(scene_audio)
                scene_video_clips.append(scene_video)

            if not scene_video_clips:
                raise RuntimeError("No scene video clips could be constructed.")

            final_video = concatenate_videoclips(scene_video_clips, method="compose")

            video_filename = f"video_{job_id}.mp4"
            output_path = STATIC_DIR / video_filename

            final_video.write_videofile(
                str(output_path),
                fps=24,
                codec="libx264",
                audio_codec="aac",
                logger=None,
            )

            if not output_path.is_file() or output_path.stat().st_size == 0:
                raise RuntimeError("Video output is missing or empty.")

            app.logger.info("Multi-scene dynamic video rendered successfully: %s", video_filename)

            return render_page(
                generated_script=script_text,
                current_script_id=script_id,
                video_filename=video_filename,
                video_ready=True,
            )

        except Exception:
            app.logger.exception("Multi-scene video rendering failed.")

            if output_path and output_path.exists():
                try:
                    output_path.unlink()
                except OSError:
                    pass

            return render_page(
                generated_script=script_text,
                current_script_id=script_id,
                error_message=(
                    "Video rendering failed. Check server logs and try again."
                ),
            ), 500

        finally:
            close_quietly(final_video)

            for sv_clip in scene_video_clips:
                close_quietly(sv_clip)

            for a_clip in scene_audio_clips_list:
                close_quietly(a_clip)

            for path in temp_files:
                try:
                    if path.exists():
                        path.unlink()
                except OSError:
                    app.logger.warning(
                        "Could not remove temporary audio file: %s",
                        path,
                        exc_info=True,
                    )

    return render_page(
        error_message="Unknown action. Please refresh and try again."
    ), 400

@app.route("/load_vault/<int:script_id>")
def load_vault(script_id):
    sess_id = get_user_session_id()
    try:
        with db_connection() as conn:
            row = conn.execute(
                "SELECT script_content FROM vault WHERE id = ? AND session_id = ?",
                (script_id, sess_id),
            ).fetchone()

        if not row:
            abort(404)

        return render_page(
            generated_script=row[0],
            current_script_id=script_id,
        )

    except sqlite3.Error:
        app.logger.exception("Failed to load a saved script.")
     
