import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. Flask Web Server for Render Port Binding ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running successfully! 🚀🤖"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 2. Telegram Bot Configuration ---
API_TOKEN = '8831853256:AAGummjGke8vPpQ85EkWYTBzig5vh291XG8'

# Aapke main channel ki ID jo screenshot se mili hai
MAIN_CHANNEL_ID = '-1004382767346' 

bot = telebot.TeleBot(API_TOKEN)

# Yahan se aap jab bhi episode ya price change karenge, wahi channel par jayega aur bot me dikhega
CURRENT_EPISODE_TITLE = "EPISODE 3504 → 3510"
TOTAL_EPISODES = "7 EPISODES"
PRICE = "₹70 ONLY"
BOT_LINK = f"https://t.me/{bot.get_me().username}"

# Main Menu / Buttons function
def send_main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup(row_width=1)
    
    markup.add(
        InlineKeyboardButton(f"🎧 EP: 3504 - 3510 ({PRICE})", callback_data="pkg_custom"),
        InlineKeyboardButton("🚀 Start / Menu", callback_data="main_menu")
    )
    
    text = (
        f"🎧 **SUPER YODDHA — Audio Series** 🚀\n\n"
        f"Aapko kaun sa episode chahiye? Neeche diye gaye button par click karein: 👇"
    )
    
    if message_id:
        try:
            bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            return
        except Exception:
            pass
            
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    send_main_menu(message.chat.id)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_user_text(message):
    user_text = message.text.strip()
    qr_image_url = "https://i.ibb.co/3m3vL05/1000018603.png"
    
    caption_text = (
        f"🎧 **SUPER YODDHA — Audio Series** 🚀\n\n"
        f"📦 **Aapka Message:** {user_text}\n"
        f"💰 **PRICE:** {PRICE}\n\n"
        f"⚡ **TURANT MILEGA!**\n\n"
        f"📲 **Payment karne ke liye upar diye gaye Barcode par Scan karke pay karein.**\n"
        f"📸 Payment karne ke baad screenshot yahan bhejen."
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
    
    bot.send_photo(
        chat_id=message.chat.id,
        photo=qr_image_url,
        caption=caption_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "main_menu":
        bot.answer_callback_query(call.id)
        send_main_menu(call.message.chat.id, call.message.message_id)
        
    elif call.data == "pkg_custom":
        bot.answer_callback_query(call.id, "Barcode & Details loaded!")
        
        qr_image_url = "https://i.ibb.co/3m3vL05/1000018603.png"
        
        caption_text = (
            f"🎧 **SUPER YODDHA — Audio Series** 🚀\n\n"
            f"📦 **{CURRENT_EPISODE_TITLE}** (Total {TOTAL_EPISODES})\n"
            f"💰 **PRICE:** {PRICE}\n\n"
            f"⚡ **TURANT MILEGA!**\n\n"
            f"📲 **Payment karne ke liye upar diye gaye Barcode par Scan karke pay karein.**\n"
            f"📸 Payment karne ke baad screenshot yahan bhejen."
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
            
        bot.send_photo(
            chat_id=call.message.chat.id,
            photo=qr_image_url,
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=markup
        )

# --- Channel par automatic post bhejne ka function ---
def post_to_main_channel():
    try:
        channel_message = (
            f"🎧 **{CURRENT_EPISODE_TITLE}**\n\n"
            f"📦 **TOTAL — {TOTAL_EPISODES}**\n\n"
            f"💰 **PRICE — {PRICE}**\n\n"
            f"⚡ **TURANT MILEGA**\n\n"
            f"📩 **Link:-** {BOT_LINK}"
        )
        bot.send_message(MAIN_CHANNEL_ID, channel_message, parse_mode="Markdown")
        print("✅ Main channel par post successfully bhej di gayi hai!")
    except Exception as e:
        print(f"⚠️ Channel par post bhejne me error aaya: {e}")

# --- 3. Main Execution with Flask Keep Alive ---
if __name__ == "__main__":
    keep_alive()
    print("🤖 Bot successfully start ho raha hai... 🚀")
    
    # Bot start hote hi channel par post bhej dega
    try:
        post_to_main_channel()
    except Exception:
        pass
        
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
