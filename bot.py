import os
import re
import telebot
from telebot import types
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# --- CONFIGURATION ---
TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389          # Aapki Admin ID
CHANNEL_ID = -1004382767346  # Aapke Super Yoddha channel ki ID
BOT_USERNAME = "ROMEO_PAY_BOT" # Aapka confirmed bot username
ADMIN_USERNAME = "Romeo_kerketta" # Aapka Telegram username help ke liye

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

app = Flask(__name__)

# --- MULTI-PACK DYNAMIC DATABASE ---
packs_db = {
    "1": {
        "title": "SUPER YODDHA — EPISODE SALE",
        "episodes": "3591 - 3595",
        "total": "5 Episodes",
        "price": "100",
        "link": "https://t.me/+zaFMdS92m5FhOGI9",
        "is_prebook": False,
        "active": True
    }
}

UPI_ID = "Badmashromeo8880@okaxis"
user_pending_pack = {}

purchased_users = {
    "1": []
}

@app.route('/')
def home():
    return "Bot is running live 24/7!"

# --- HELPER FUNCTION: Calculate Total Episodes Automatically ---
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

# --- ADMIN COMMAND: Add Pack with Automatic Episode Counting ---
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
            
        mode_text = "Pre-Booking Pack" if is_prebook else "Instant Delivery Pack"
        bot.reply_to(message, f"✅ {mode_text} {pack_id} successfully added/updated!\nEpisodes: {episodes}\nTotal: {calculated_total}\nPrice: ₹{price}")
    except Exception as e:
        bot.reply_to(message, "⚠️ Galat format!\nInstant ke liye: `/addpack 1 | 3561 - 3569 | 150 | link`\nPre-book ke liye: `/addpack 2 | 3570 - 3575 | 150 | link | pre`", parse_mode="Markdown")

# --- ADMIN COMMAND: Edit Existing Pack Anytime ---
@bot.message_handler(commands=['editpack'])
def edit_pack(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=1)[1].split('|')
        pack_id = parts[0].strip()
        episodes = parts[1].strip()
        price = parts[2].strip()
        link = parts[3].strip()
        
        if pack_id not in packs_db:
            bot.reply_to(message, f"⚠️ Pack ID '{pack_id}' database mein nahi mili! Pehle /addpack use karein.")
            return
            
        is_prebook = packs_db[pack_id]["is_prebook"]
        if len(parts) > 4 and parts[4].strip().lower() == 'pre':
            is_prebook = True
        elif len(parts) > 4 and parts[4].strip().lower() == 'instant':
            is_prebook = False
            
        calculated_total = calculate_total_episodes(episodes)
        title = "SUPER YODDHA — PRE-BOOKING" if is_prebook else "SUPER YODDHA — EPISODE SALE"
        
        packs_db[pack_id].update({
            "title": title,
            "episodes": episodes,
            "total": calculated_total,
            "price": price,
            "link": link,
            "is_prebook": is_prebook
        })
        
        bot.reply_to(message, f"✅ Pack {pack_id} successfully updated!\nEpisodes: {episodes}\nTotal: {calculated_total}\nPrice: ₹{price}")
    except Exception as e:
        bot.reply_to(message, "⚠️ Galat format!\nUse karein: `/editpack 1 | 3561 - 3575 | 200 | https://t.me/+link`", parse_mode="Markdown")

# --- ADMIN COMMAND: Toggle Pack ---
@bot.message_handler(commands=['toggle'])
def toggle_pack(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Kripya Pack ID likhein. Format: `/toggle 1`", parse_mode="Markdown")
            return
            
        pack_id = parts[1].strip()
        if pack_id in packs_db:
            packs_db[pack_id]["active"] = not packs_db[pack_id]["active"]
            status = "ACTIVE (Enable)" if packs_db[pack_id]["active"] else "HIDDEN (Disable)"
            bot.reply_to(message, f"✅ Pack {pack_id} ka status badal kar ho gaya hai: *{status}*", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"⚠️ Pack ID '{pack_id}' database mein nahi mili!")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error aa gaya: {e}")

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
            if data["is_prebook"]:
                btn_text = f"⏳ Pre-Book Now | EP- {data['episodes']}"
            else:
                btn_text = f"✨ Buy Episodes | EP- {data['episodes']}"
            
            btn = types.InlineKeyboardButton(btn_text, callback_data=f"buy_{pack_id}")
            markup.add(btn)
            
    if not active_packs_found:
        bot.reply_to(message, "⚠️ Filhal koi bhi pack active nahi hai.")
        return

    welcome_text = (
        "🔥 SUPER YODDHA — EPISODES 🔥\n\n"
        "Niche diye gaye packs mein se select karein:\n\n"
        "*(Agar koi madad chahiye ho toh 'help' likh kar bhejein)*"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- HELP HANDLER ---
@bot.message_handler(func=lambda message: message.text and message.text.lower() in ["help", "/help"])
def help_command(message):
    help_text = (
        "🛠️ *PAYMENT & SUPPORT HELP*\n\n"
        "Agar aapko payment verify hone mein koi samasya aa rahi hai, ya link nahi mila hai, toh aap seedha admin se sampark kar sakte hain:\n\n"
        f"👉 Admin Contact: @{ADMIN_USERNAME}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Admin Se Baat Karein", url=f"https://t.me/{ADMIN_USERNAME}"))
    bot.reply_to(message, help_text, parse_mode="Markdown", reply_markup=markup)

# --- HELPER FUNCTION: QR Code ---
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
    
    if is_prebook:
        mode_label = "PRE-BOOKING QR CODE"
        note_text = "1. Payment ke baad screenshot bhejein.\n2. Release hote hi link bhej diya jayega."
    else:
        mode_label = "INSTANT PAYMENT QR CODE"
        note_text = "1. Payment ke baad screenshot bhejein.\n2. Turant link mil jayega."
    
    caption = (
        f"⚡ PACK {pack_id} — {mode_label} ⚡\n\n"
        f"• UPI ID: {UPI_ID}\n"
        f"• Amount: ₹{price}\n"
        f"• Episodes: {episodes} ({total})\n\n"
        f"{note_text}\n\n"
        f"*(Madad ke liye 'help' likh kar bhej sakte hain)*"
    )
    
    try:
        bot.send_photo(chat_id, qr_url, caption=caption, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, f"{caption}\n\n⚠️ QR Code error: {e}", parse_mode="Markdown")

# --- ADMIN COMMAND: Send All Active Packs to Channel ---
@bot.message_handler(commands=['allpost'])
def send_all_packs_to_channel(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    active_count = 0
    for pack_id, data in packs_db.items():
        if data["active"]:
            try:
                markup = types.InlineKeyboardMarkup()
                btn_text = "⏳ Pre-Book Now" if data["is_prebook"] else "✨ Buy Episodes"
                bot_url = f"https://t.me/{BOT_USERNAME}?start=buy_{pack_id}"
                markup.add(types.InlineKeyboardButton(btn_text, url=bot_url))
                
                delivery_text = "⏳ PRE-BOOKING" if data["is_prebook"] else "⚡ INSTANT DELIVERY"
                text = f"✅ EPISODES {data['episodes']} 🦋\n\n🎧 TOTAL — {data['total']} 🦋\n\n{delivery_text} 🦋"
                
                bot.send_message(CHANNEL_ID, text, reply_markup=markup)
                active_count += 1
            except Exception as e:
                print(f"Error sending pack {pack_id}: {e}")
                
    if active_count > 0:
        bot.reply_to(message, f"✅ Total {active_count} active packs ki post main channel par bhej di gayi hai!")
    else:
        bot.reply_to(message, "⚠️ Koi bhi active pack nahi mila!")

# --- CHANNEL POST COMMAND (Supports Photo or Audio with caption) ---
@bot.message_handler(content_types=['photo', 'audio'], commands=['post'])
def post_pack_media(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.content_type == 'text':
        try:
            parts = message.text.split(maxsplit=2)
            pack_id = parts[1].strip()
            custom_link = parts[2].strip()
            
            if pack_id not in packs_db:
                bot.reply_to(message, "⚠️ Invalid Pack ID!")
                return
                
            packs_db[pack_id]["link"] = custom_link
            data = packs_db[pack_id]
            
            markup = types.InlineKeyboardMarkup()
            btn_text = "⏳ Pre-Book Now" if data["is_prebook"] else "✨ Buy Episodes"
            bot_url = f"https://t.me/{BOT_USERNAME}?start=buy_{pack_id}"
            markup.add(types.InlineKeyboardButton(btn_text, url=bot_url))
            
            delivery_text = "⏳ PRE-BOOKING" if data["is_prebook"] else "⚡ INSTANT DELIVERY"
            text = f"✅ EPISODES {data['episodes']} 🦋\n\n🎧 TOTAL — {data['total']} 🦋\n\n{delivery_text} 🦋"
            
            bot.send_message(CHANNEL_ID, text, reply_markup=markup)
            notify_buyers(pack_id, custom_link)
            bot.reply_to(message, "✅ Text post channel par bhej di gayi hai!")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Galat format! Use karein:\n`/post 1 https://t.me/+your_link`", parse_mode="Markdown")
            
    else:
        try:
            caption_text = message.caption or ""
            parts = caption_text.split()
            if len(parts) < 2:
                bot.reply_to(message, "⚠️ Kripya media ke caption mein Pack ID aur Link likhein. Jaise: `1 https://t.me/+link`")
                return
                
            pack_id = parts[0].strip()
            custom_link = parts[1].strip()
            
            if pack_id not in packs_db:
                bot.reply_to(message, "⚠️ Invalid Pack ID!")
                return
                
            packs_db[pack_id]["link"] = custom_link
            data = packs_db[pack_id]
            
            markup = types.InlineKeyboardMarkup()
            btn_text = "⏳ Pre-Book Now" if data["is_prebook"] else "✨ Buy Episodes"
            bot_url = f"https://t.me/{BOT_USERNAME}?start=buy_{pack_id}"
            markup.add(types.InlineKeyboardButton(btn_text, url=bot_url))
            
            delivery_text = "⏳ PRE-BOOKING" if data["is_prebook"] else "⚡ INSTANT DELIVERY"
            text = f"✅ EPISODES {data['episodes']} 🦋\n\n🎧 TOTAL — {data['total']} 🦋\n\n{delivery_text} 🦋"
            
            file_id = message.photo[-1].file_id if message.photo else message.audio.file_id
            
            if message.photo:
                bot.send_photo(CHANNEL_ID, file_id, caption=text, reply_markup=markup)
            elif message.audio:
                bot.send_audio(CHANNEL_ID, file_id, caption=text, reply_markup=markup)
                
            notify_buyers(pack_id, custom_link)
            bot.reply_to(message, "✅ Media post channel par bhej di gayi hai!")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Error: {e}")

def notify_buyers(pack_id, link):
    data = packs_db[pack_id]
    if pack_id in purchased_users:
        for user_id in purchased_users[pack_id]:
            try:
                bot.unban_chat_member(CHANNEL_ID, user_id, only_if_banned=True)
                if data["is_prebook"]:
                    bot.send_message(user_id, f"🎉 Aapke pre-booked episodes (Ep: {data['episodes']}) release ho gaye hain! Yeh raha link:\n\n{link}")
                else:
                    bot.send_message(user_id, f"📢 Nayi post channel par daal di gayi hai! Yeh raha aapka link:\n\n{link}")
            except Exception as ex:
                print(f"Could not message user {user_id}: {ex}")

# --- UNIVERSAL CALLBACK HANDLER FOR BUTTONS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    if call.data.startswith("buy_"):
        bot.answer_callback_query(call.id)
        pack_id = call.data.split("_")[1]
        send_qr_to_user(call.message.chat.id, pack_id)
    elif call.data.startswith("approve_") or call.data.startswith("reject_"):
        handle_admin_action_direct(call)

def handle_admin_action_direct(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
        return
        
    data_parts = call.data.split('_')
    action = data_parts[0]
    
    if action == 'approve':
        pack_id = data_parts[1]
        target_user_id = int(data_parts[2])
        
        if pack_id in packs_db:
            if target_user_id not in purchased_users[pack_id]:
                purchased_users[pack_id].append(target_user_id)
        
        bot.answer_callback_query(call.id, f"Pack {pack_id} Approved!", show_alert=True)
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + f"\n\nSTATUS: ✅ APPROVED (PACK {pack_id})")
        except:
            pass
            
        data = packs_db.get(pack_id, {})
        is_prebook = data.get("is_prebook", False)
        link = data.get("link", "https://t.me/")
        
        try:
            bot.unban_chat_member(CHANNEL_ID, target_user_id, only_if_banned=True)
        except Exception as e:
            print(f"Auto-add error: {e}")

        if is_prebook:
            bot.send_message(target_user_id, "🎉 Aapka pre-booking payment verify ho gaya hai! Jaise hi episodes release honge, aapko channel mein add kar diya jayega.")
        else:
            bot.send_message(target_user_id, f"🎉 Aapka payment verify ho gaya hai! Aapko channel mein add kar diya gaya hai. Link: {link}")
        
    else:
        target_user_id = int(data_parts[1])
        bot.answer_callback_query(call.id, "Payment Rejected!", show_alert=True)
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ❌ REJECTED")
        except:
            pass
            
        bot.send_message(target_user_id, "❌ Aapka payment screenshot reject kar diya gaya hai. Kripya sahi screenshot bhejein (Madad ke liye 'help' likhein).")

# --- SCREENSHOT HANDLER ---
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    if message.chat.id == ADMIN_ID:
        return
        
    user = message.from_user
    bot.reply_to(message, "✅ Aapka screenshot mil gaya hai! Verification ke liye admin ke paas bhej diya gaya hai. *(Agar koi samasya ho toh 'help' likhein)*", parse_mode="Markdown")
    
    pack_id = user_pending_pack.get(user.id, "1")
    data = packs_db.get(pack_id, {})
    episodes = data.get("episodes", "N/A")
    total = data.get("total", "N/A")
    price = data.get("price", "N/A")
    
    username_text = f"@{user.username}" if user.username else "N/A"
    
    caption = (
        "🚨 NEW PAYMENT SCREENSHOT RECEIVED! 🚨\n\n"
        f"• Name: {user.first_name}\n"
        f"• User ID: {user.id}\n"
        f"• Username: {username_text}\n"
        f"• Selected Pack: Pack {pack_id} (Ep: {episodes} [{total}] - ₹{price})\n\n"
        "👇 Approve karne ke liye click karein:"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"⚡️ Approve Pack {pack_id}", callback_data=f"approve_{pack_id}_{user.id}"))
    markup.add(types.InlineKeyboardButton("❌ Reject Payment", callback_data=f"reject_{user.id}"))
    
    try:
        photo_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, photo_id, caption=caption, reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Error forwarding photo: {e}")

# --- APSCHEDULER SETUP ---
scheduler = BackgroundScheduler()
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    import threading
    polling_thread = threading.Thread(target=bot.infinity_polling, daemon=True)
    polling_thread.start()
    
    app.run(host='0.0.0.0', port=port)
    
