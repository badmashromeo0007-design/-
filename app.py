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
    Flask,
    render_template,
    request,
    session,
    send_from_directory,
    abort,
)

from groq import Groq
from werkzeug.utils import secure_filename

from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ColorClip
from moviepy.video.compositing.concatenate import concatenate_videoclips


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR_VALUE = os.environ.get("DATA_DIR", "").strip()
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

if not DATA_DIR_VALUE:
    raise RuntimeError("DATA_DIR environment variable is required.")

if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "FLASK_SECRET_KEY must contain at least 32 characters."
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
    MAX_CONTENT_LENGTH=1024 * 1024,
    MAX_FORM_MEMORY_SIZE=256 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=(
        os.environ.get(
            "SESSION_COOKIE_SECURE", "true"
        ).lower() == "true"
    ),
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app.logger.setLevel(logging.INFO)

client = Groq(
    api_key=GROQ_API_KEY,
    timeout=60.0,
    max_retries=1,
)

MAX_STORY_LENGTH = 10000
MAX_SCRIPT_LENGTH = 20000
MAX_DIALOGUES = 100

VIDEO_PATTERN = re.compile(
    r"^video_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\.mp4$"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

@contextmanager
def db_connection():

    conn = sqlite3.connect(
        str(DB_PATH),
        timeout=20,
    )

    try:
        conn.execute("PRAGMA busy_timeout = 20000")
        conn.execute("PRAGMA foreign_keys = ON")

        yield conn

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# =========================================================
# DATABASE INITIALIZATION AND MIGRATION
# =========================================================

def init_db():

    with db_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                title TEXT NOT NULL,
                script_content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migrate older vault tables safely.
        columns = [
            column[1]
            for column in conn.execute(
                "PRAGMA table_info(vault)"
            ).fetchall()
        ]

        if "session_id" not in columns:

            conn.execute("""
                ALTER TABLE vault
                ADD COLUMN session_id TEXT DEFAULT 'legacy_session'
            """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                filename TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        video_columns = [
            column[1]
            for column in conn.execute(
                "PRAGMA table_info(videos)"
            ).fetchall()
        ]

        if "session_id" not in video_columns:
            raise RuntimeError(
                "Existing videos table has no session_id column. "
                "Back up and migrate this table before starting."
            )

        if "filename" not in video_columns:
            raise RuntimeError(
                "Existing videos table has no filename column."
            )

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_vault_session
            ON vault(session_id, id DESC)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_videos_session
            ON videos(session_id, filename)
        """)

    app.logger.info("Database initialization completed.")


init_db()


# =========================================================
# SESSION MANAGEMENT
# =========================================================

def get_user_session_id():

    session_id = session.get("user_session_id")

    if (
        not isinstance(session_id, str)
        or not re.fullmatch(r"[0-9a-f]{32}", session_id)
    ):

        session_id = secrets.token_hex(16)
        session["user_session_id"] = session_id

    return session_id


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
        {
            "id": row[0],
            "title": row[1],
            "content": row[2],
        }
        for row in rows
    ]


# =========================================================
# CSRF PROTECTION
# =========================================================

@app.context_processor
def inject_csrf_token():

    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    return {
        "csrf_token": session["csrf_token"]
    }


def valid_csrf():

    submitted = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")

    return bool(
        submitted
        and expected
        and secrets.compare_digest(submitted, expected)
    )


# =========================================================
# SECURITY HEADERS
# =========================================================

@app.after_request
def add_security_headers(response):

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    response.headers["Cache-Control"] = "no-store"

    return response


# =========================================================
# PRIVATE VIDEO OWNERSHIP
# =========================================================

def get_verified_video_path(filename):

    safe_name = secure_filename(filename or "")

    if not safe_name or not VIDEO_PATTERN.fullmatch(safe_name):
        abort(404)

    sess_id = get_user_session_id()

    with db_connection() as conn:

        row = conn.execute("""
            SELECT id
            FROM videos
            WHERE filename = ?
              AND session_id = ?
        """, (
            safe_name,
            sess_id,
        )).fetchone()

    if not row:
        abort(404)

    video_path = STATIC_DIR / safe_name

    if not video_path.is_file():
        abort(404)

    return safe_name


# =========================================================
# VOICE SELECTION
# =========================================================

def get_voice(character):

    character = character.lower()

    if "narrator" in character:

        return os.environ.get(
            "NARRATOR_VOICE",
            "hi-IN-MadhurNeural",
        )

    female_names = (
        "xun er",
        "xun'er",
        "medusa",
        "queen",
        "cai lin",
        "qingshan",
    )

    if any(name in character for name in female_names):

        return os.environ.get(
            "FEMALE_VOICE",
            "hi-IN-SwaraNeural",
        )

    return os.environ.get(
        "MALE_VOICE",
        "hi-IN-MadhurNeural",
    )


# =========================================================
# SCRIPT PARSER
# =========================================================

def parse_script_into_scenes(script_text):

    scenes = []

    current_scene = {
        "title": "Scene 1",
        "visual": "Atmospheric cinematic opening",
        "dialogues": [],
    }

    total_dialogues = 0

    for raw_line in script_text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        upper_line = line.upper()

        if upper_line.startswith(("[SCENE", "SCENE ")):

            if current_scene["dialogues"]:
                scenes.append(current_scene)

            current_scene = {
                "title": line,
                "visual": "Cinematic transition view",
                "dialogues": [],
            }

            continue

        if upper_line.startswith("VISUAL:"):

            current_scene["visual"] = line.split(
                ":", 1
            )[1].strip()

            continue

        if ":" not in line:
            continue

        character, dialogue = line.split(":", 1)

        character = character.strip().strip("*_ ")
        dialogue = dialogue.strip().strip("*_ ")

        if not character or not dialogue:
            continue

        if character.lower().startswith(
            ("episode ", "chapter ")
        ):
            continue

        current_scene["dialogues"].append(
            (dialogue, get_voice(character))
        )

        total_dialogues += 1

        if total_dialogues >= MAX_DIALOGUES:
            break

    if current_scene["dialogues"]:
        scenes.append(current_scene)

    return scenes


# =========================================================
# VISUAL MOOD COLORS
# =========================================================

def get_mood_color_from_visual(visual_text):

    vt = (visual_text or "").lower()

    if any(word in vt for word in (
        "fire", "crimson", "red", "anger",
        "flame", "battle", "fight",
    )):
        return (42, 18, 24)

    if any(word in vt for word in (
        "forest", "emerald", "green",
        "nature", "tree", "plant", "calm",
    )):
        return (18, 40, 30)

    if any(word in vt for word in (
        "night", "dark", "shadow",
        "navy", "mystic", "cave",
    )):
        return (18, 32, 45)

    if any(word in vt for word in (
        "purple", "royal", "energy",
        "aura", "spirit", "breakthrough",
    )):
        return (38, 24, 45)

    return (24, 28, 36)


# =========================================================
# AUDIO GENERATION
# =========================================================

async def create_audio_files(dialogues, output_paths):

    semaphore = asyncio.Semaphore(3)

    async def generate_one(dialogue, voice, path):

        async with semaphore:

            communicate = edge_tts.Communicate(
                dialogue,
                voice,
            )

            await communicate.save(str(path))

    tasks = [
        generate_one(dialogue, voice, path)
        for (dialogue, voice), path
        in zip(dialogues, output_paths)
    ]

    await asyncio.gather(*tasks)


# =========================================================
# RESOURCE CLEANUP
# =========================================================

def close_quietly(resource):

    if resource is None:
        return

    try:
        resource.close()

    except Exception:
        app.logger.warning(
            "Could not close media resource.",
            exc_info=True,
        )


# =========================================================
# PAGE RENDERING
# =========================================================

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

        app.logger.exception(
            "Could not load Script Vault."
        )

        saved_scripts = []

        if not error_message:
            error_message = (
                "Script Vault is temporarily unavailable."
            )

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


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(413)
def request_too_large(error):

    return render_page(
        error_message="Request too large. Shorten your story."
    ), 413


@app.errorhandler(404)
def not_found(error):

    return "Not found", 404


@app.errorhandler(403)
def forbidden(error):

    return "Access denied", 403


@app.errorhandler(500)
def internal_error(error):

    app.logger.exception("Internal server error.")

    return render_page(
        error_message="An internal server error occurred."
    ), 500


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health", methods=["GET"])
def health():

    try:

        with db_connection() as conn:
            conn.execute("SELECT 1").fetchone()

        return "OK", 200

    except sqlite3.Error:

        app.logger.exception("Health check failed.")

        return "Database unavailable", 503


# =========================================================
# MAIN ROUTE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "GET":
        return render_page()

    if not valid_csrf():

        return render_page(
            error_message=(
                "Session expired. Refresh the page and try again."
            )
        ), 400

    action = request.form.get(
        "action", ""
    ).strip()

    story_input = request.form.get(
        "story_input", ""
    ).strip()

    sess_id = get_user_session_id()

    # -----------------------------------------------------
    # GENERATE SCRIPT
    # -----------------------------------------------------

    if action == "generate_script":

        if not story_input:

            return render_page(
                error_message="Please enter a story."
            ), 400

        if len(story_input) > MAX_STORY_LENGTH:

            return render_page(
                error_message=(
                    "Story limit is 10,000 characters."
                ),
                story_input=story_input[:MAX_STORY_LENGTH],
            ), 400

        prompt = f"""
You are a cinematic anime screenplay writer.

Write a Hindi/Hinglish screenplay based on the user's story.

Preserve character consistency, emotional tone and scene continuity.

Use this format:

[SCENE 1: Scene Title]
VISUAL: Scene description
Narrator: Dialogue
Character Name: Dialogue

Make the screenplay cinematic and engaging.

Story:
{story_input}
"""

        try:

            model_name = os.environ.get(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile",
            )

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.8,
                max_tokens=6000,
            )

            generated_script = (
                response.choices[0].message.content or ""
            ).strip()

            if not generated_script:
                raise ValueError("Empty model response.")

            generated_script = generated_script[
                :MAX_SCRIPT_LENGTH
            ]

            title = (
                story_input.splitlines()[0][:80]
                if story_input.splitlines()
                else "Cinematic Script"
            )

            with db_connection() as conn:

                cursor = conn.execute("""
                    INSERT INTO vault (
                        session_id,
                        title,
                        script_content
                    )
                    VALUES (?, ?, ?)
                """, (
                    sess_id,
                    title,
                    generated_script,
                ))

                script_id = cursor.lastrowid

            return render_page(
                generated_script=generated_script,
                current_script_id=script_id,
                story_input=story_input,
            )

        except Exception:

            app.logger.exception(
                "Script generation failed."
            )

            return render_page(
                error_message=(
                    "Script generation failed. Try again later."
                ),
                story_input=story_input,
            ), 500

    # -----------------------------------------------------
    # GENERATE VIDEO
    # -----------------------------------------------------

    if action == "generate_video":

        script_id_raw = request.form.get(
            "script_id", ""
        ).strip()

        if not script_id_raw.isdigit():

            return render_page(
                error_message="Invalid script ID."
            ), 400

        script_id = int(script_id_raw)

        try:

            with db_connection() as conn:

                row = conn.execute("""
                    SELECT script_content
                    FROM vault
                    WHERE id = ?
                      AND session_id = ?
                """, (
                    script_id,
                    sess_id,
                )).fetchone()

        except sqlite3.Error:

            app.logger.exception(
                "Could not retrieve script."
            )

            return render_page(
                error_message="Database error."
            ), 500

        if not row:

            return render_page(
                error_message="Script not found."
            ), 404

        script_text = row[0]

        if len(script_text) > MAX_SCRIPT_LENGTH:

            return render_page(
                generated_script=script_text,
                current_script_id=script_id,
                error_message="Script is too long.",
            ), 400

        scenes = parse_script_into_scenes(script_text)

        if not scenes or not any(
            scene["dialogues"] for scene in scenes
        ):

            return render_page(
                generated_script=script_text,
                current_script_id=script_id,
                error_message=(
                    "No valid dialogue found. "
                    "Use Character: Dialogue format."
                ),
            ), 400

        job_id = uuid.uuid4()

        video_filename = f"video_{job_id}.mp4"
        output_path = STATIC_DIR / video_filename

        temp_files = []
        source_audio_clips = []
        combined_audio_clips = []
        video_clips = []

        scene_audio_clips = {}
        final_video = None

        try:

            # Flatten dialogues and preserve scene mapping.
            flat_dialogues = []
            dialogue_mapping = []

            for scene_in
