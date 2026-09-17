import os
import telebot
from telebot import types
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# --- CONFIGURATION ---
TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389          # Aapki Admin ID
CHANNEL_ID = -1004382767346  # Aapke Super Yoddha channel ki ID

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

app = Flask(__name__)

# --- MULTI-PACK DYNAMIC DATABASE ---
packs_db = {
    "1": {
        "title": "SUPER YODDHA — EPISODE SALE",
        "episodes": "3549 To 3554",
        "total": "6 Episodes",
        "price": "50",
        "link": "https://t.me/+ebSSIzOxKfRmNWU9",
        "active": True
    },
    "2": {
        "title": "SUPER YODDHA — EPISODE SALE",
        "episodes": "3555 To 3560",
        "total": "6 Episodes",
        "price": "80",
        "link": "https://t.me/+AnotherUniqueLinkHere",
        "active": False
    }
}

UPI_ID = "badmashromeo0007@okaxis"

@app.route('/')
def home():
    return "Bot is running live 24/7!"

# --- ADMIN COMMAND: Naya Pack Add karne ke liye ---
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
        
        packs_db[pack_id] = {
            "title": "SUPER YODDHA — EPISODE SALE",
            "episodes": episodes,
            "total": "6 Episodes",
            "price": price,
            "link": link,
            "active": True
        }
        bot.reply_to(message, f"✅ Pack {pack_id} successfully added/updated!\nEpisodes: {episodes}\nPrice: ₹{price}")
    except Exception as e:
        bot.reply_to(message, "⚠️ Galat format! Use karein:\n`/addpack 2 | 3555-3560 | 80 | https://t.me/link`", parse_mode="Markdown")

# --- ADMIN COMMAND: Pack ko Hide/Unhide karne ke liye ---
@bot.message_handler(commands=['toggle'])
def toggle_pack(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        pack_id = message.text.split(maxsplit=1)[1].strip()
        if pack_id in packs_db:
            packs_db[pack_id]["active"] = not packs_db[pack_id]["active"]
            status = "ACTIVE (Dikh raha hai)" if packs_db[pack_id]["active"] else "HIDDEN (Chhup gaya hai)"
            bot.reply_to(message, f"✅ Pack {pack_id} status changed to: *{status}*", parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ Yeh Pack ID nahi mili!")
    except Exception as e:
        bot.reply_to(message, "⚠️ Format: `/toggle 2`", parse_mode="Markdown")

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    
    active_packs_found = False
    for pack_id, data in packs_db.items():
        if data["active"]:
            active_packs_found = True
            btn = types.InlineKeyboardButton(f"🎧 Pack {pack_id} (Ep: {data['episodes']} - ₹{data['price']})", callback_data=f"buy_{pack_id}")
            markup.add(btn)
            
    if not active_packs_found:
        bot.reply_to(message, "⚠️ Filhal koi bhi pack active nahi hai.")
        return

    welcome_text = (
        "🔥 **SUPER YODDHA — EPISODE SALE** 🔥\n\n"
        "Niche diye gaye packs mein se apna pasandeeda pack select karein:"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- CHANNEL POST COMMAND ---
@bot.message_handler(commands=['post'])
def post_pack(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        pack_id = message.text.split(maxsplit=1)[1].strip()
        if pack_id not in packs_db:
            bot.reply_to(message, "⚠️ Invalid Pack ID!")
            return
            
        data = packs_db[pack_id]
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(f"✨ Buy Episodes (₹{data['price']})", callback_data=f"buy_{pack_id}")
        markup.add(btn)
        
        text = (
            f"🔥 **{data['title']}** 🔥\n\n"
            f"🎧 **Episode:** {data['episodes']}\n\n"
            f"📦 **Total:** {data['total']}\n\n"
            f"💰 **Price:** ₹{data['price']}\n\n"
            f"⚡️ **Turant Saare Episodes Mil Jayenge!**"
        )
        bot.send_message(CHANNEL_ID, text, reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(message, f"✅ Post successfully channel par bhej di gayi hai!")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: Format use karein `/post 1` ya `/post 2`\n(Ensure karein ki bot channel par admin ho)", parse_mode="Markdown")

# --- CALLBACK FOR BUY BUTTONS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    bot.answer_callback_query(call.id)
    pack_id = call.data.split("_")[1]
    
    if pack_id not in packs_db:
        return
        
    data = packs_db[pack_id]
    price = data["price"]
    episodes = data["episodes"]
    
    upi_string = f"upi://pay?pa={UPI_ID}&pn=Romeo&am={price}&cu=INR"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_string}"
    
    caption = (
        f"⚡ **PACK {pack_id} PAYMENT QR CODE** ⚡\n\n"
        f"• UPI ID: `{UPI_ID}`\n"
        f"• Amount: ₹{price}\n"
        f"• Episodes: {episodes}\n\n"
        "1. Is QR code ko kisi bhi UPI app se scan karein.\n"
        "2. Payment karne ke baad screenshot yahin bot mein bhej dein."
    )
    
    try:
        bot.send_photo(call.message.chat.id, qr_url, caption=caption, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"{caption}\n\n⚠️ QR Code error: {e}")

# --- SCREENSHOT HANDLER (Instant Pop-up Alert ke sath) ---
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user = message.from_user
    bot.reply_to(message, "✅ Aapka screenshot mil gaya hai! Verification ke liye admin ke paas bhej diya gaya hai.")
    
    caption = (
        "🚨 **NEW PAYMENT SCREENSHOT RECEIVED!** 🚨\n\n"
        f"• Name: {user.first_name}\n"
        f"• User ID: `{user.id}`\n"
        f"• Username: @{user.username if user.username else 'N/A'}\n\n"
        "👇 *Niche diye gaye pack ko select karke turant approve karein:*"
    )
    
    markup = types.InlineKeyboardMarkup()
    for pack_id in packs_db.keys():
        markup.add(types.InlineKeyboardButton(f"⚡️ Approve Pack {pack_id}", callback_data=f"approve_{pack_id}_{user.id}"))
    markup.add(types.InlineKeyboardButton("❌ Reject Payment", callback_data=f"reject_{user.id}"))
    
    try:
        photo_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, photo_id, caption=caption, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Error forwarding photo: {e}")

# --- ADMIN APPROVAL HANDLER ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_admin_action(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
        return
        
    data_parts = call.data.split('_')
    action = data_parts[0]
    
    if action == 'approve':
        pack_id = data_parts[1]
        target_user_id = int(data_parts[2])
        
        bot.answer_callback_query(call.id, f"Pack {pack_id} Approved Successfully!", show_alert=True)
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + f"\n\nSTATUS: ✅ APPROVED (PACK {pack_id})")
        except:
            pass
            
        link = packs_db.get(pack_id, {}).get("link", "https://t.me/")
        bot.send_message(target_user_id, f"🎉 Aapka payment verify ho gaya hai! Yeh raha aapka link:\n{link}")
        
    else:
        target_user_id = int(data_parts[1])
        bot.answer_callback_query(call.id, "Payment Rejected!", show_alert=True)
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ❌ REJECTED")
        except:
            pass
        bot.send_message(target_user_id, "❌ Aapka payment screenshot reject kar diya gaya hai.")

# --- APSCHEDULER SETUP ---
scheduler = BackgroundScheduler()
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    import threading
    polling_thread = threading.Thread(target=bot.infinity_polling, daemon=True)
    polling_thread.start()
    
    app.run(host='0.0.0.0', port=port)
    
