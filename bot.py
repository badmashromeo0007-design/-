import os
import time
import logging
from flask import Flask
from threading import Thread
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)

# --- 1. Flask Web Server for Render Port Binding ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running successfully! 🚀🤖"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Flask server on port {port}...")
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
PAYMENT_AMOUNT = '30'
PAYEE_NAME = 'SuperYoddha'

# Direct UPI Payment Link
UPI_INTENT_LINK = f"upi://pay?pa={YOUR_UPI_ID}&pn={PAYEE_NAME}&am={PAYMENT_AMOUNT}&cu=INR&tn=SuperYoddhaEpisodes"

bot = telebot.TeleBot(API_TOKEN)

try:
    bot.set_my_commands([
        BotCommand("start", "🚀 Start / Main Menu"),
        BotCommand("menu", "🎛 Open Menu")
    ])
    print("Bot commands set successfully.")
except Exception as e:
    print(f"Menu commands error: {e}")

FULL_TITLE = "EPISODE 3503 → 3510"
TOTAL_EPISODES = "TOTAL — 8 EPISODES"
PRICE_TEXT = "PRICE — ₹30 ONLY"

def get_start_text():
    return (
        f"🎧 **{FULL_TITLE}**\n\n"
        f"📦 **{TOTAL_EPISODES}**\n\n"
        f"💰 **{PRICE_TEXT}**\n\n"
        f"⚡ **Payment Karne Ka Tarika:**\n"
        f"1. Neeche diye gaye **'Pay ₹30 Now'** button par click karein (GPay/PhonePe/Paytm khul jayega).\n"
        f"2. Payment karne ke baad **screenshot** yahin chat me bhejiye!\n\n"
        f"*(Agar button se app na khule, toh aap is UPI ID par bhej sakte hain: `{YOUR_UPI_ID}`)*"
    )

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    print(f"Received /start or /menu from user: {message.from_user.id}")
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("⚡ Pay ₹30 Now (GPay/PhonePe)", url=UPI_INTENT_LINK))
    markup.add(InlineKeyboardButton("💬 Admin se Baat Karein", url=f"https://t.me/{ADMIN_USERNAME}"))
    
    bot.send_message(
        chat_id=message.chat.id,
        text=get_start_text(),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    print(f"Received photo payment screenshot from user: {message.from_user.id}")
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
    print(f"Received text message: {message.text}")
    bot.reply_to(message, "📷 Kripya payment karne ke baad apna **screenshot** yahan bhejiye taaki aapko episodes ka link mil sake!")

if __name__ == "__main__":
    print("Initializing Flask server...")
    keep_alive()
    
    print("Connecting to Telegram...")
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"Webhook removal error: {e}")

    print("Starting bot polling loop...")
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling crashed with error: {e}")
            print("Restarting polling in 5 seconds...")
            time.sleep(5)
            
