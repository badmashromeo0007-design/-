import os
import sqlite3
import logging
import secrets
from urllib.parse import urlencode
from contextlib import contextmanager

import requests
from flask import Flask, request, jsonify, abort

# ================= CONFIGURATION (Directly Set) =================

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("episode-bot")

# Aapke diye gaye details yahan direct set kar diye gaye hain:
TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389
CHANNEL_ID = -1004382767346
RENDER_URL = "https://badmash-4k97.onrender.com"

# Webhook aur Setup ke liye secure random/custom secrets
WEBHOOK_SECRET = "my_super_secret_webhook_key_12345"
SETUP_SECRET = "my_super_secure_setup_key_12345"

UPI_ID = "Badmashromeo0007@okaxis"
UPI_NAME = "Romeo"

DATABASE_PATH = "/var/data/bot.sqlite3"

INITIAL_EPISODES = "3623 - 3630"
INITIAL_PRICE = 160
INITIAL_CHANNEL_LINK = "https://t.me/A_ToolsX"

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
HTTP = requests.Session()


# ================= DATABASE =================

@contextmanager
def db():
    folder = os.path.dirname(DATABASE_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH, timeout=20)
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA busy_timeout=20000")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TEXT,
                admin_message_id INTEGER,
                payment_message_id INTEGER
            )
        """)

        defaults = {
            "episodes": INITIAL_EPISODES,
            "price": str(INITIAL_PRICE),
            "channel_link": INITIAL_CHANNEL_LINK,
        }

        for key, value in defaults.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings(key, value) "
                "VALUES (?, ?)",
                (key, value),
            )


def get_setting(key):
    with db() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        ).fetchone()

    return row["value"] if row else ""


def update_settings(episodes, price, link):
    with db() as conn:
        conn.executemany("""
            INSERT INTO settings(key, value) VALUES (?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
        """, [
            ("episodes", episodes),
            ("price", str(price)),
            ("channel_link", link),
        ])


# ================= TELEGRAM API =================

def tg(method, payload=None):
    response = HTTP.post(
        f"{TELEGRAM_API}/{method}",
        json=payload or {},
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(
            f"Telegram {method}: {result}"
        )

    return result.get("result")


def send_message(chat_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if keyboard:
        payload["reply_markup"] = keyboard

    return tg("sendMessage", payload)


def send_photo(chat_id, photo_url, caption):
    return tg("sendPhoto", {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
    })


def edit_message(chat_id, message_id, text):
    return tg("editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    })


def answer_callback(callback_id, text=""):
    try:
        payload = {"callback_query_id": callback_id}
        if text:
            payload["text"] = text[:200]
        tg("answerCallbackQuery", payload)
    except Exception:
        log.exception("Callback response failed")


# ================= PACK MESSAGES =================

def buy_keyboard():
    episodes = get_setting("episodes")
    price = int(get_setting("price") or "160")

    return {
        "inline_keyboard": [[{
            "text": (
                f"🟢 Buy Episodes | "
                f"EP ({episodes} - ₹{price})"
            ),
            "callback_data": "buy_episodes",
        }]]
    }


def default_post_text():
    episodes = get_setting("episodes")
    price = get_setting("price")

    return (
        f"𝗘𝗣𝗜𝗦𝗢𝗗𝗘 — {episodes}\n\n"
        f"📦 𝗧𝗢𝗧𝗔𝗟 — {episodes}\n\n"
        f"💰 𝗣𝗥𝗜𝗖𝗘 — ₹{price} ✅\n\n"
        "⚡️ पेमेंट करके स्क्रीनशॉट DM करें।\n"
        "🚀 Payment verify hone ke baad "
        "channel link bheja jayega."
    )


# ================= UPI QR =================

def make_qr_url(amount):
    upi_uri = "upi://pay?" + urlencode({
        "pa": UPI_ID,
        "pn": UPI_NAME,
        "am": str(amount),
        "cu": "INR",
    })

    return (
        "https://api.qrserver.com/v1/create-qr-code/?"
        + urlencode({
            "size": "300x300",
            "data": upi_uri,
        })
    )


def send_payment_details(user_id):
    amount = int(get_setting("price") or "160")
    episodes = get_setting("episodes")

    caption = (
        "🛍 PAYMENT DETAILS\n\n"
        f"📦 Episodes Pack: {episodes}\n"
        f"💰 Total Amount: ₹{amount}\n\n"
        f"📱 UPI ID: {UPI_ID}\n\n"
        "UPI app se payment karein. Payment ke baad "
        "screenshot isi bot ko DM karein.\n"
        "Admin payment verify karega."
    )

    try:
        send_photo(
            user_id,
            make_qr_url(amount),
            caption,
        )
    except Exception:
        log.exception("QR image sending failed")
        send_message(user_id, caption)


# ================= PAYMENT REVIEW =================

def forward_payment_for_review(message, user_id):
    tg("forwardMessage", {
        "chat_id": ADMIN_ID,
        "from_chat_id": user_id,
        "message_id": message["message_id"],
    })

    with db() as conn:
        cursor = conn.execute("""
            INSERT INTO payments(
                user_id, status, payment_message_id
            )
            VALUES (?, 'pending', ?)
        """, (user_id, message["message_id"]))

        payment_id = cursor.lastrowid

    keyboard = {
        "inline_keyboard": [[
            {
                "text": "✅ Approve",
                "callback_data": f"approve_{payment_id}",
            },
            {
                "text": "❌ Reject",
                "callback_data": f"reject_{payment_id}",
            },
        ]]
    }

    admin_notice = send_message(
        ADMIN_ID,
        "🔔 NEW PAYMENT SCREENSHOT\n\n"
        f"User ID: {user_id}\n"
        f"Request ID: #{payment_id}",
        keyboard,
    )

    with db() as conn:
        conn.execute("""
            UPDATE payments
            SET admin_message_id = ?
            WHERE id = ?
        """, (admin_notice["message_id"], payment_id))


def review_payment(callback, approved):
    actor_id = callback.get("from", {}).get("id")

    if actor_id != ADMIN_ID:
        answer_callback(
            callback["id"],
            "Only admin can review payments.",
        )
        return

    try:
        payment_id = int(
            callback.get("data", "").split("_", 1)[1]
        )
    except (ValueError, IndexError):
        answer_callback(callback["id"], "Invalid request.")
        return

    with db() as conn:
        row = conn.execute(
            "SELECT * FROM payments WHERE id = ?",
            (payment_id,),
        ).fetchone()

        if not row:
            answer_callback(callback["id"], "Request not found.")
            return

        if row["status"] != "pending":
            answer_callback(
                callback["id"],
                f"Already {row['status']}.",
            )
            return

        status = "approved" if approved else "rejected"

        cursor = conn.execute("""
            UPDATE payments
            SET status = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
        """, (status, payment_id))

        if cursor.rowcount != 1:
            answer_callback(callback["id"], "Already reviewed.")
            return

    if approved:
        link = get_setting("channel_link")

        if not link:
            send_message(
                ADMIN_ID,
                "⚠️ Payment marked approved, but channel link "
                "is missing. Configure it with /addpack.",
            )
            answer_callback(callback["id"], "Link is missing.")
            return

        try:
            send_message(
                row["user_id"],
                "🎉 Aapka payment admin ne approve kar diya hai!\n\n"
                f"Channel link:\n{link}",
            )
        except Exception:
            log.exception("Could not send invite link to user")
            send_message(
                ADMIN_ID,
                f"⚠️ Approved, but user {row['user_id']} "
                "could not be messaged.",
            )

        final_text = "✅ Payment approved by admin."

    else:
        try:
            send_message(
                row["user_id"],
                "❌ Aapka payment reject kar diya gaya hai. "
                "Kripya valid payment screenshot bhejein.",
            )
        except Exception:
            log.exception("Could not notify rejected user")

        final_text = "❌ Payment rejected by admin."

    message = callback.get("message") or {}

    try:
        edit_message(
            message["chat"]["id"],
            message["message_id"],
            final_text,
        )
    except Exception:
        log.exception("Could not edit review message")

    answer_callback(callback["id"], "Done.")


# ================= CALLBACK BUTTONS =================

def handle_callback(callback):
    data = callback.get("data", "")

    if data == "buy_episodes":
        user_id = callback.get("from", {}).get("id")
        answer_callback(callback["id"])

        if not user_id:
            return

        try:
            send_payment_details(user_id)
        except Exception:
            log.exception("Could not send payment details")
            try:
                send_message(
                    callback["message"]["chat"]["id"],
                    "Payment details lene ke liye pehle "
                    "bot ko private chat mein /start bhejein.",
                )
            except Exception:
                pass

        return

    if data.startswith("approve_"):
        review_payment(callback, approved=True)
        return

    if data.startswith("reject_"):
        review_payment(callback, approved=False)
        return

    answer_callback(callback["id"], "Unknown action.")


# ================= MEDIA POSTING =================

def post_admin_media(message):
    episodes = get_setting("episodes")
    price = get_setting("price")

    title = (
        message.get("caption")
        or f"EPISODE — {episodes}"
    ).strip()

    caption = (
        f"🎧 {title}\n\n"
        f"📦 𝗧𝗢𝗧𝗔𝗟 — {episodes}\n"
        f"💰 𝗣𝗥𝗜𝗖𝗘 — ₹{price} ✅\n\n"
        "⚡️ पेमेंट करके स्क्रीनशॉट DM करें。\n"
        "Payment verification ke baad link milega."
    )[:1024]

    if message.get("audio"):
        method = "sendAudio"
        media_key = "audio"
    elif message.get("voice"):
        method = "sendVoice"
        media_key = "voice"
    elif message.get("document"):
        method = "sendDocument"
        media_key = "document"
    else:
        return False

    tg(method, {
        "chat_id": CHANNEL_ID,
        media_key: message[media_key]["file_id"],
        "caption": caption,
        "reply_markup": buy_keyboard(),
    })

    return True


# ================= MESSAGE COMMANDS =================

def handle_message(message):
    sender = message.get("from", {})
    user_id = sender.get("id")
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()

    if not user_id or chat_id is None:
        return

    # /start
    if text == "/start" or text.startswith("/start "):
        send_message(
            chat_id,
            default_post_text(),
            buy_keyboard(),
        )
        return

    # /addpack and /setpack
    if user_id == ADMIN_ID and (
        text.startswith("/addpack")
        or text.startswith("/setpack")
    ):
        try:
            _, _, args = text.partition(" ")
            parts = [part.strip() for part in args.split("|")]

            if len(parts) != 3:
                raise ValueError("Expected 3 fields")

            episodes, price_text, link = parts
            price = int(price_text)

            if not episodes or price <= 0:
                raise ValueError("Invalid episode range or price")

            if not link.startswith("https://t.me/"):
                raise ValueError("Invalid Telegram invite link")

            update_settings(episodes, price, link)

            send_message(
                chat_id,
                "✅ Pack updated successfully!\n\n"
                f"📦 Episodes: {episodes}\n"
                f"💰 Price: ₹{price}\n"
                f"🔗 Link: {link}",
            )

        except (ValueError, TypeError):
            send_message(
                chat_id,
                "⚠️ Correct format:\n"
                "/addpack 3743 - 3748 | 160 | "
                "https://t.me/+YOUR_INVITE",
            )

        return

    # /post
    if user_id == ADMIN_ID and text.startswith("/post"):
        content = text[len("/post"):].strip()
        if not content:
            content = default_post_text()

        try:
            send_message(CHANNEL_ID, content, buy_keyboard())
            send_message(chat_id, "✅ Post channel par bhej di gayi.")
        except Exception:
            log.exception("Channel post failed")
            send_message(
                chat_id,
                "❌ Post failed. Bot channel admin hai ya nahi check karein.",
            )

        return

    # /reply USER_ID message
    if user_id == ADMIN_ID and text.startswith("/reply"):
        try:
            _, target, reply_text = text.split(" ", 2)
            target_id = int(target)

            if not reply_text.strip():
                raise ValueError("Empty reply")

            send_message(
                target_id,
                f"💬 Admin Message:\n\n{reply_text}",
            )
            send_message(chat_id, "✅ Message user ko bhej diya.")

        except (ValueError, TypeError):
            send_message(
                chat_id,
                "⚠️ Format: /reply USER_ID Your message",
            )
        except Exception:
            log.exception("Admin reply failed")
            send_message(
                chat_id,
                "❌ Message deliver nahi hua. User ne bot "
                "start kiya hai ya nahi check karein.",
            )

        return

    # Admin sends audio, voice or document
    if user_id == ADMIN_ID and any(
        key in message for key in ("audio", "voice", "document")
    ):
        try:
            post_admin_media(message)
            send_message(chat_id, "✅ Media channel par post ho gaya.")
        except Exception:
            log.exception("Media posting failed")
            send_message(
                chat_id,
                "❌ Media post nahi hua. Render logs aur "
                "channel permissions check karein.",
            )

        return

    # User submits payment screenshot/document
    if user_id != ADMIN_ID and (
        "photo" in message or "document" in message
    ):
        try:
            forward_payment_for_review(message, user_id)
            send_message(
                chat_id,
                "⏳ Screenshot admin ko bhej diya gaya hai. "
                "Verification ka wait karein.",
            )
        except Exception:
            log.exception("Payment submission failed")
            send_message(
                chat_id,
                "❌ Screenshot submit nahi hua. Thodi der baad "
                "dobara try karein.",
            )

        return


# ================= WEBHOOK =================

@app.get("/")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/webhook")
def webhook():
    supplied = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token", ""
    )

    if not secrets.compare_digest(supplied, WEBHOOK_SECRET):
        abort(403)

    update = request.get_json(silent=True)

    if not isinstance(update, dict):
        return jsonify({"ok": False}), 400

    try:
        if "callback_query" in update:
            handle_callback(update["callback_query"])
        elif "message" in update:
            handle_message(update["message"])
    except Exception:
        log.exception("Update handling failed")

    return jsonify({"ok": True}), 200


# ================= WEBHOOK SETUP =================

@app.post("/set_webhook")
def set_webhook():
    supplied = request.headers.get("X-Setup-Secret", "")

    if not secrets.compare_digest(supplied, SETUP_SECRET):
        abort(403)

    result = tg("setWebhook", {
        "url": f"{RENDER_URL}/webhook",
        "secret_token": WEBHOOK_SECRET,
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": False,
    })

    return jsonify({"ok": True, "result": result})


@app.post("/delete_webhook")
def delete_webhook():
    supplied = request.headers.get("X-Setup-Secret", "")

    if not secrets.compare_digest(supplied, SETUP_SECRET):
        abort(403)

    result = tg("deleteWebhook", {
        "drop_pending_updates": False,
    })

    return jsonify({"ok": True, "result": result})


# Initialize persistent settings and payment database.
init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
                )
    
