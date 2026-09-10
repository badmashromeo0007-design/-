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
    
    # Package Buttons
    markup.add(
        InlineKeyboardButton("🎧 EP: 3487 - 3491 (₹50)", callback_data="pkg_3487_3491"),
        InlineKeyboardButton("🎧 EP: 3491 - 3495 (₹80)", callback_data="pkg_3491_3495"),
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
        
    elif call.data.startswith("pkg_"):
        bot.answer_callback_query(call.id, "Package selected!")
        
        # Package ke hisab se exact details aur response text
        if "3504_3510" in call.data:
            response = (
                "🎧 **EPISODE 3504 → 3510** 🚀\n\n"
                "📦 **TOTAL — 7 EPISODES** 📚\n\n"
                "💰 **PRICE — ₹70 ONLY** 💵\n\n"
                "⚡ **TURANT MILEGA** 🔥\n\n"
                "📩 **DM:** @ROMEO_KERKETTA"
            )
        elif "3491_3495" in call.data:
            response = (
                "🎧 **EPISODE 3491 → 3495** 🚀\n\n"
                "📦 **TOTAL — 5 EPISODES** 📚\n\n"
                "💰 **PRICE — ₹80 ONLY** 💵\n\n"
                "⚡ **TURANT MILEGA** 🔥\n\n"
                "📩 **DM:** @ROMEO_KERKETTA"
            )
        else:
            response = (
                "🎧 **EPISODE 3487 → 3491** 🚀\n\n"
                "📦 **TOTAL — 5 EPISODES** 📚\n\n"
                "💰 **PRICE — ₹50 ONLY** 💵\n\n"
                "⚡ **TURANT MILEGA** 🔥\n\n"
                "📩 **DM:** @ROMEO_KERKETTA"
            )
            
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⭐ Pay with Stars / Order Now", callback_data="pay_stars"))
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        
        try:
            bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
        except Exception:
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "pay_stars":
        bot.answer_callback_query(call.id, "Processing...")
        text_message = (
            "⭐ **PAYMENT & DELIVERY** 💳\n\n"
            "🛡️ Episodes pane ke liye turant yahan message karein:\n"
            "📩 **Admin DM:** @ROMEO_KERKETTA"
        )
        bot.send_message(call.message.chat.id, text_message, parse_mode="Markdown")

# --- 3. Main Execution with Flask Keep Alive ---
if __name__ == "__main__":
    keep_alive()
    print("🤖 Bot successfully start ho raha hai... 🚀")
    bot.infinity_polling(skip_pending=True)
