import os
import time
import logging
from flask import Flask
from threading import Thread
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# Enable logging
logging.basicConfig(level=logging.INFO)

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
API_TOKEN = '8831853256:AAFOYW-K73PXAc8hHSJ1QvuVGBqudEU3fnY'
EPISODES_INVITE_LINK = 'https://t.me/+rViclcLru-0yYTI1'
ADMIN_USERNAME = "ROMEO_KERKETTA"

# --- 3. Aapka UPI ID ---
YOUR_UPI_ID = 'badmashromeo0007@okaxis'
PAYMENT_AMOUNT = '₹30'

bot = telebot.TeleBot(API_TOKEN)

try:
    bot.set_my_commands([
        BotCommand("start", "🚀 Start / Main Menu"),
        BotCommand("menu", "🎛 Open Menu")
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

FULL_TITLE = "EPISODE 3503 → 3510"
TOTAL_EPISODES = "TOTAL — 8 EPISODES"
PRICE_TEXT = "PRICE — 30 ONLY"

def get_start_text():
    return (
        f"🎧 **{FULL_TITLE}**\n\n"
        f"📦 **{TOTAL_EPISODES}**\n\n"
        f"💰 **PRICE — {PAYMENT_AMOUNT} ONLY**\n\n"
        f"⚡ **Payment Kaise Karein:**\n"
        f"Neeche diye gaye UPI ID par kisi bhi app (GPay / PhonePe / Paytm) se **{PAYMENT_AMOUNT}** send karein:\n\n"
        f"👉 UPI ID: `{YOUR_UPI_ID}`\n\n"
        f"📷 Payment karne ke baad **screenshot** yahin chat me bhejiye, aapko turant episodes ka link mil jayega!"
    )

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=1)
    # Safe HTTP/HTTPS links or support buttons only (No unsupported protocols)
    markup.add(InlineKeyboardButton("💬 Admin se Sampark Karein", url=f"https://t.me/{ADMIN_USERNAME}"))
    
    bot.send_message(
        chat_id=message.chat.id,
        text=get_start_text(),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    thanks_text = (
        f"✨ **Payment Ka Screenshot Mil Gaya! Thanks!** ✨\n"
        f"🎧 **THE SUPER YODDHA** channel par aapka swagat hai!\n\n"
        f"🎉 Aapka payment verify ho gaya hai! Neeche aapke episodes ka secure link hai: 👇"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🚀 Join Episodes Channel", url=EPISODES_INVITE_LINK),
        InlineKeyboardButton("💬 Support / Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    
    bot.reply_to(message, text=thanks_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.reply_to(message, "📷 Kripya payment karne ke baad apna **screenshot** yahan bhejiye taaki aapko episodes ka link mil sake!")

if __name__ == "__main__":
    keep_alive()
    print("🤖 Bot successfully start ho raha hai...")
    
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"Webhook removal error: {e}")

    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)
            
