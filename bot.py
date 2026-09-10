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
STORAGE_CHANNEL_ID = '-1003621158878'

bot = telebot.TeleBot(API_TOKEN)

# Main Menu / Buttons function
def send_main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Sirf naya package button aur menu button
    markup.add(
        InlineKeyboardButton("🎧 EP: 3504 - 3510 (₹70)", callback_data="pkg_3504_3510"),
        InlineKeyboardButton("🚀 Start / Menu", callback_data="main_menu")
    )
    
    text = (
        "🎧 **SUPER YODDHA — Audio Series** 🚀\n\n"
        "Aapko kaun sa episode chahiye? Neeche diye gaye button par click karein: 👇"
    )
    
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    send_main_menu(message.chat.id)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    send_main_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "main_menu":
        bot.answer_callback_query(call.id)
        send_main_menu(call.message.chat.id, call.message.message_id)
        
    elif call.data == "pkg_3504_3510":
        bot.answer_callback_query(call.id, "QR Code & Details loaded!")
        
        # Scanner image URL (Aapke diye gaye Google Pay QR code ki link)
        qr_image_url = "https://i.ibb.co/3m3vL05/1000018603.png"
        
        caption_text = (
            "🎧 **SUPER YODDHA — Audio Series** 🚀\n\n"
            "📦 **EPISODE:** 3504 → 3510 (Total 7 Episodes)\n"
            "💰 **PRICE:** ₹70 ONLY\n\n"
            "⚡ **TURANT MILEGA!**\n\n"
            "📲 **Payment karne ke liye upar diye gaye QR Code par Scan karke ₹70 pay karein.**\n"
            "📸 Payment karne ke baad screenshot yahan bhejen:\n"
            "📩 **Admin DM:** @ROMEO_KERKETTA"
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        
        try:
            # Purana text message delete karke QR code aur caption bhetega
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

# --- 3. Main Execution with Flask Keep Alive ---
if __name__ == "__main__":
    keep_alive()
    print("🤖 Bot successfully start ho raha hai... 🚀")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
