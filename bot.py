import os
import re
import telebot
from telebot import types
from flask import Flask, request

# --- CONFIGURATION ---
TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389          # Aapki Admin ID
CHANNEL_ID = -1004382767346  # Aapke Super Yoddha channel ki ID
BOT_USERNAME = "ROMEO_PAY_BOT" # Aapka confirmed bot username
ADMIN_USERNAME = "Romeo_kerketta" # Aapka Telegram username help ke liye

# ✅ Aapke Render URL se set kiya gaya app name
RENDER_APP_NAME = "badmash-4k97" 

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- MULTI-PACK DYNAMIC DATABASE ---
packs_db = {
    "1": {
        "title": "SUPER YODDHA — EPISODE SALE",
        "episodes": "3608 - 3612",
        "total": "5 Episodes",
        "price": "120",
        "link": "https://t.me/+gy8gewj0snllZThl",
        "is_prebook": False,
        "active": True
    }
}

UPI_ID = "Badmashromeo0007@okaxis"
user_pending_pack = {}
purchased_users = {"1": []}

@app.route('/')
def home():
    return "Bot webhook is active and live!"

# --- WEBHOOK ROUTE FOR RENDER ---
@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "Invalid request", 403

# --- HELPER: Calculate Total Episodes ---
def calculate_total_episodes(episodes_str):
    try:
        numbers = re.findall(r'\d+', episodes_str)
        if len(numbers) >= 2:
            start_ep = int(numbers[0])
            end_ep = int(numbers[1])
            total = (end_ep - start_ep) + 1
            if total > 0:
                return f"{total} Episodes"
    except Exception as e:
        print(f"Calculation error: {e}")
    return "5 Episodes"

# --- ADMIN COMMAND: Add Pack ---
@bot.message_handler(commands=['addpack'])
def add_pack(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=1)[1].split('|')
        pack_id = parts[0].strip()
        episodes = parts[1].strip()
        price = parts[2].strip()
        link = parts[3].strip()
        
        is_prebook = False
        if len(parts) > 4 and parts[4].strip().lower() == 'pre':
            is_prebook = True
            
        calculated_total = calculate_total_episodes(episodes)
        title = "SUPER YODDHA — PRE-BOOKING" if is_prebook else "SUPER YODDHA — EPISODE SALE"
        
        packs_db[pack_id] = {
            "title": title,
            "episodes": episodes,
            "total": calculated_total,
            "price": price,
            "link": link,
            "is_prebook": is_prebook,
            "active": True
        }
        if pack_id not in purchased_users:
            purchased_users[pack_id] = []
            
        bot.reply_to(message, f"✅ Pack {pack_id} successfully added/updated!\nEpisodes: {episodes}\nPrice: ₹{price}")
    except Exception as e:
        bot.reply_to(message, "⚠️ Galat format! Use karein:\n`/addpack 1 | 3608 - 3612 | 120 | https://t.me/+link`", parse_mode="Markdown")

# --- START & MENU COMMAND ---
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    text_args = message.text.split()
    if len(text_args) > 1 and text_args[1].startswith("buy_"):
        pack_id = text_args[1].split("_")[1]
        if pack_id in packs_db:
            send_qr_to_user(message.chat.id, pack_id)
            return

    markup = types.InlineKeyboardMarkup()
    active_packs_found = False
    for pack_id, data in packs_db.items():
        if data["active"]:
            active_packs_found = True
            btn_text = f"⏳ Pre-Book Now | EP- {data['episodes']}" if data["is_prebook"] else f"✨ Buy Episodes | EP- {data['episodes']}"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"buy_{pack_id}"))
            
    if not active_packs_found:
        bot.reply_to(message, "⚠️ Filhal koi bhi pack active nahi hai.")
        return

    welcome_text = "🔥 SUPER YODDHA — EPISODES 🔥\n\nNiche diye gaye packs mein se select karein:"
    bot.reply_to(message, welcome_text, reply_markup=markup)

# --- HELP HANDLER ---
@bot.message_handler(func=lambda message: message.text and message.text.lower() in ["help", "/help"])
def help_command(message):
    help_text = f"🛠️ *PAYMENT & SUPPORT HELP*\n\nAdmin se sampark karein:\n👉 @{ADMIN_USERNAME}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Admin Se Baat Karein", url=f"https://t.me/{ADMIN_USERNAME}"))
    bot.reply_to(message, help_text, parse_mode="Markdown", reply_markup=markup)

# --- QR CODE SENDER ---
def send_qr_to_user(chat_id, pack_id):
    if pack_id not in packs_db:
        return
        
    user_pending_pack[chat_id] = pack_id
    data = packs_db[pack_id]
    price = data["price"]
    episodes = data["episodes"]
    total = data["total"]
    is_prebook = data["is_prebook"]
    
    upi_string = f"upi://pay?pa={UPI_ID}&pn=Romeo&am={price}&cu=INR"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_string}"
    
    note_text = "1. Payment ke baad screenshot bhejein.\n2. Release hote hi link bhej diya jayega." if is_prebook else "1. Payment ke baad screenshot bhejein.\n2. Turant link mil jayega."
    mode_label = "PRE-BOOKING QR CODE" if is_prebook else "INSTANT PAYMENT QR CODE"
    
    caption = (
        f"⚡ PACK {pack_id} — {mode_label} ⚡\n\n"
        f"• UPI ID: {UPI_ID}\n"
        f"• Amount: ₹{price}\n"
        f"• Episodes: {episodes} ({total})\n\n"
        f"{note_text}"
    )
    
    try:
        bot.send_photo(chat_id, qr_url, caption=caption)
    except Exception as e:
        bot.send_message(chat_id, f"{caption}\n\n⚠️ QR Error: {e}")

# --- CHANNEL POST HANDLER ---
@bot.message_handler(content_types=['photo', 'audio', 'document'])
def handle_media_post(message):
    if message.chat.id == ADMIN_ID and message.caption and message.caption.startswith("/post"):
        try:
            parts = message.caption.split()
            pack_id = parts[1].strip() if len(parts) > 1 else "1"
            
            if pack_id not in packs_db:
                bot.reply_to(message, f"⚠️ Pack ID '{pack_id}' database mein nahi hai!")
                return
                
            data = packs_db[pack_id]
            
            markup = types.InlineKeyboardMarkup()
            btn_text = f"⏳ Pre-Book Now | EP- {data['episodes']}" if data["is_prebook"] else f"✨ Buy Episodes | EP- {data['episodes']}"
            bot_url = f"https://t.me/{BOT_USERNAME}?start=buy_{pack_id}"
            markup.add(types.InlineKeyboardButton(btn_text, url=bot_url))
            
            delivery_text = "⏳ PRE-BOOKING" if data["is_prebook"] else "⚡ INSTANT DELIVERY"
            text = f"✅ EPISODES {data['episodes']} 🦋\n\n🎧 TOTAL — {data['total']} 🦋\n\n{delivery_text} 🦋"
            
            if message.photo:
                bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=text, reply_markup=markup)
            elif message.audio:
                bot.send_audio(CHANNEL_ID, message.audio.file_id, caption=text, reply_markup=markup)
            elif message.document:
                bot.send_document(CHANNEL_ID, message.document.file_id, caption=text, reply_markup=markup)
                
            bot.reply_to(message, "✅ Post successfully channel par bhej di gayi hai!")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Post error: {e}")
        return

    # User Screenshot Handler
    if message.chat.id != ADMIN_ID and message.photo:
        user = message.from_user
        bot.reply_to(message, "✅ Screenshot mil gaya hai! Verification ke liye admin ke paas bhej diya gaya hai.")
        
        pack_id = user_pending_pack.get(user.id, "1")
        data = packs_db.get(pack_id, {})
        
        caption = (
            "🚨 NEW PAYMENT SCREENSHOT 🚨\n\n"
            f"• Name: {user.first_name}\n"
            f"• User ID: {user.id}\n"
            f"• Pack: Pack {pack_id} (₹{data.get('price', '120')})\n\n"
            "👇 Action lein:"
        )
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"⚡️ Approve Pack {pack_id}", callback_data=f"approve_{pack_id}_{user.id}"))
        markup.add(types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}"))
        
        try:
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup)
        except Exception as e:
            bot.send_message(ADMIN_ID, f"⚠️ Error: {e}")

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Answer callback error: {e}")

    try:
        if call.data.startswith("buy_"):
            pack_id = call.data.split("_")[1]
            send_qr_to_user(call.message.chat.id, pack_id)
            
        elif call.data.startswith("approve_"):
            parts = call.data.split("_")
            pack_id = parts[1]
            target_user_id = int(parts[2])
            
            if call.from_user.id != ADMIN_ID:
                bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
                return
                
            if pack_id in purchased_users and target_user_id not in purchased_users[pack_id]:
                purchased_users[pack_id].append(target_user_id)
            
            try:
                bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + f"\n\nSTATUS: ✅ APPROVED (PACK {pack_id})")
            except Exception as e:
                print(f"Caption edit error: {e}")
                
            data = packs_db.get(pack_id, {})
            link = data.get("link", "https://t.me/")
            
            try:
                bot.unban_chat_member(CHANNEL_ID, target_user_id, only_if_banned=True)
            except Exception as e:
                print(e)
                
            bot.send_message(target_user_id, f"🎉 Aapka payment verify ho gaya hai! Yeh raha channel ka link:\n\n{link}")
            
        elif call.data.startswith("reject_"):
            parts = call.data.split("_")
            target_user_id = int(parts[1])
            
            if call.from_user.id != ADMIN_ID:
                bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
                return
                
            try:
                bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + f"\n\nSTATUS: ❌ REJECTED")
            except Exception as e:
                print(f"Caption edit error: {e}")
                
            bot.send_message(target_user_id, f"❌ Aapka payment screenshot reject kar diya gaya hai. Kripya sahi screenshot bhejein.")
    except Exception as e:
        print(f"Callback execution error: {e}")

# --- WEBHOOK SETUP & RUN ---
if __name__ == '__main__':
    bot.remove_webhook()
    webhook_url = f"https://{RENDER_APP_NAME}.onrender.com/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"Webhook explicitly set to: {webhook_url}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
