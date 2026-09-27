import os
from flask import Flask, request
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN", "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1004382767346")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6817248389"))
RENDER_URL = os.getenv("RENDER_URL", "https://badmash-4k97.onrender.com")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# Default Database variables
TOTAL_EPISODES = "3623 - 3630"
PACK_PRICE = 160
CHANNEL_LINK = "https://t.me/+2Bq6yb6hSeBhOTJI"

# --- 1. FLASK WEBHOOK SETUP ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        handle_update(update)
    return "OK", 200

def handle_update(update):
    global TOTAL_EPISODES, PACK_PRICE, CHANNEL_LINK
    
    # Callback Query (Inline Buttons)
    if "callback_query" in update:
        cq = update["callback_query"]
        data = cq["data"]
        chat_id = cq["message"]["chat"]["id"]
        message_id = cq["message"]["message_id"]
        
        if data == "buy_episodes":
            upi_id = "Badmashromeo0007@okaxis"
            amount = PACK_PRICE if PACK_PRICE > 0 else 160
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa={upi_id}&pn=Romeo&am={amount}&cu=INR"
            
            caption = (
                f"🛍 **Payment Details**\n\n"
                f"📦 Episodes Pack: **{TOTAL_EPISODES}**\n"
                f"💰 Total Amount: **₹{amount}**\n\n"
                f"📱 Scan the QR code above using any UPI app (GPay, PhonePe, Paytm).\n"
                f"⚠️ *Payment ke baad screenshot ishi bot ko bhej dein verification ke liye!*"
            )
            send_photo(chat_id, qr_url, caption)
            
        elif data.startswith("approve_"):
            user_id = data.split("_")[1]
            send_message(user_id, f"🎉 Aapka payment verify ho gaya hai! Yeh raha channel ka link:\n\n{CHANNEL_LINK}")
            edit_message_text(chat_id, message_id, "✅ **Payment Approved Successfully by Admin.**")
            
        elif data.startswith("reject_"):
            user_id = data.split("_")[1]
            send_message(user_id, "❌ **Aapka payment reject kar diya gaya hai.** Kripya sahi screenshot ya valid payment bhejien.")
            edit_message_text(chat_id, message_id, "❌ **Payment Rejected.**")
            
        elif data.startswith("reply_user_"):
            target_user = data.split("_")[2]
            send_message(chat_id, f"✍️ Us user ko jawab dene ke liye yeh command use karein:\n`/reply {target_user} Aapka message...`")
            
        return

    # Message Handling
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        
        # --- UPDATE PACK, RANGE, PRICE & LINK VIA /addpack OR /setpack ---
        if (text.startswith("/addpack") or text.startswith("/setpack")) and user_id == ADMIN_ID:
            try:
                if "|" in text:
                    parts = [p.strip() for p in text.replace("/addpack", "").replace("/setpack", "").split("|")]
                    pack_no = parts[0]
                    episode_range = parts[1]
                    price = int(parts[2])
                    new_link = parts[3]
                else:
                    parts = text.split(" ")
                    episode_range = parts[1]
                    price = int(parts[2])
                    new_link = parts[3]
                
                TOTAL_EPISODES = episode_range
                PACK_PRICE = price
                CHANNEL_LINK = new_link
                
                send_message(chat_id, 
                    f"✅ **Pack successfully update ho gaya hai!**\n\n"
                    f"📦 Episodes: **{TOTAL_EPISODES}**\n"
                    f"💰 Price: **₹{PACK_PRICE}**\n"
                    f"🔗 Link: {CHANNEL_LINK}"
                )
            except Exception:
                send_message(chat_id, "⚠️ Format galat hai! Sahi tarika:\n`/addpack 1 | 3623 - 3630 | 160 | https://t.me/+xxxx`")
            return

        # 2. Manual Post Command (/post)
        if text.startswith("/post") and user_id == ADMIN_ID:
            post_content = text.replace("/post", "").strip()
            if not post_content:
                post_content = (
                    f"𝗘𝗣𝗜𝗦𝗢𝗗𝗘 — {TOTAL_EPISODES}\n\n"
                    f"📦 𝗧𝗢𝗧𝗔𝗟 — {TOTAL_EPISODES}\n\n"
                    f"💰 𝗣𝗥𝗜𝗖𝗘 — ₹{PACK_PRICE} ✅\n\n"
                    f"⚡️ पेमेंट करके स्क्रीनशॉट DM करें。\n"
                    f"🚀 पेमेंट कन्फर्म होते ही एपिसोड तुरंत मिल जाएगा।"
                )
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": f"🟢 Buy Episodes | EP ({TOTAL_EPISODES} - ₹{PACK_PRICE})", "callback_data": "buy_episodes"}]
                ]
            }
            send_message_with_keyboard(CHANNEL_ID, post_content, keyboard)
            send_message(chat_id, "✅ Post successfully channel par bhej di gayi hai!")
            return

        # 3. Interactive Reply System (/reply command)
        if text.startswith("/reply") and user_id == ADMIN_ID:
            try:
                parts = text.split(" ", 2)
                target_user_id = parts[1]
                reply_text = parts[2]
                send_message(target_user_id, f"💬 **Admin Message:**\n\n{reply_text}")
                send_message(chat_id, "✅ Message user tak pahunch gaya hai.")
            except Exception:
                send_message(chat_id, "⚠️ Format: `/reply [user_id] [message]`")
            return

        # 4. Direct MP3/Audio Posting
        if user_id == ADMIN_ID and ("audio" in message or "document" in message or "voice" in message):
            file_id = message.get("audio", {}).get("file_id") or \
                      message.get("document", {}).get("file_id") or \
                      message.get("voice", {}).get("file_id")
            
            user_caption = message.get("caption")
            if not user_caption:
                user_caption = f"EPISODE — {TOTAL_EPISODES}"

            caption = (
                f"🎧 **{user_caption}**\n\n"
                f"📦 𝗧𝗢𝗧𝗔𝗟 — {TOTAL_EPISODES}\n"
                f"💰 𝗣𝗥𝗜𝗖𝗘 — ₹{PACK_PRICE} ✅\n\n"
                f"⚡️ पेमेंट करके स्क्रीनशॉट DM करें。\n"
                f"🚀 पेमेंट कन्फर्म होते ही एपिसोड तुरंत मिल जाएगा。"
            )
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": f"🟢 Buy Episodes | EP ({TOTAL_EPISODES} - ₹{PACK_PRICE})", "callback_data": "buy_episodes"}]
                ]
            }
            
            send_audio_to_channel(CHANNEL_ID, file_id, caption, keyboard)
            send_message(chat_id, "✅ Audio file channel par post ho gayi hai!")
            return

        # 5. Payment Verification & Approval (User sending screenshot)
        if user_id != ADMIN_ID and ("photo" in message or "document" in message):
            forward_to_admin(message, user_id)
            send_message(chat_id, "⏳ Aapka payment screenshot admin ke paas bhej diya gaya hai. Kripya verification ka wait karein.")
            return

        # Start Command
        if text == "/start":
            welcome_msg = (
                f"𝗘𝗣𝗜𝗦𝗢𝗗𝗘 — {TOTAL_EPISODES}\n\n"
                f"📦 𝗧𝗢𝗧𝗔𝗟 — {TOTAL_EPISODES}\n\n"
                f"💰 𝗣𝗥𝗜𝗖𝗘 — ₹{PACK_PRICE} ✅\n\n"
                f"⚡️ पेमेंट करके स्क्रीनशॉट DM करें。\n"
                f"🚀 पेमेंट कन्फर्म होते ही एपिसोड तुरंत मिल जाएगा。"
            )
            keyboard = {
                "inline_keyboard": [
                    [{"text": f"🟢 Buy Episodes | EP ({TOTAL_EPISODES} - ₹{PACK_PRICE})", "callback_data": "buy_episodes"}]
                ]
            }
            send_message_with_keyboard(chat_id, welcome_msg, keyboard)

# --- HELPER FUNCTIONS FOR TELEGRAM API ---
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_message_with_keyboard(chat_id, text, keyboard):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "reply_markup": keyboard, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_photo(chat_id, photo_url, caption):
    url = f"{TELEGRAM_API}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def edit_message_text(chat_id, message_id, text):
    url = f"{TELEGRAM_API}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def forward_to_admin(message, user_id):
    url = f"{TELEGRAM_API}/forwardMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "from_chat_id": user_id,
        "message_id": message["message_id"]
    }
    requests.post(url, json=payload)
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve_{user_id}"},
                {"text": "❌ Reject", "callback_data": f"reject_{user_id}"}
            ],
            [
                {"text": "💬 Reply to User", "callback_data": f"reply_user_{user_id}"}
            ]
        ]
    }
    send_message_with_keyboard(ADMIN_ID, f"🔔 New Payment Screenshot received from user ID: `{user_id}`", keyboard)

def send_audio_to_channel(channel_id, file_id, caption, keyboard):
    url = f"{TELEGRAM_API}/sendAudio"
    payload = {
        "chat_id": channel_id,
        "audio": file_id,
        "caption": caption,
        "reply_markup": keyboard,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# --- WEBHOOK SETTER ---
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    webhook_url = f"{RENDER_URL}/{TOKEN}"
    response = requests.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}")
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    
