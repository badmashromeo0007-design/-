import os
from flask import Flask
from threading import Thread
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

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

# --- 3. Aapki UPI ID (Yahan apni asli UPI ID daalein) ---
YOUR_UPI_ID = 'your_upi@okaxis'  # <-- Apna asli UPI ID yahan likhein (jaise 9876543210@paytm)
PAYMENT_AMOUNT = '30'
PAYEE_NAME = 'SuperYoddha'

# Direct UPI Payment Link (Jo Google Pay, PhonePe, Paytm sabhi me open hoga)
UPI_INTENT_LINK = f"upi://pay?pa={YOUR_UPI_ID}&pn={PAYEE_NAME}&am={PAYMENT_AMOUNT}&cu=INR&tn=SuperYoddhaEpisodes"

bot = telebot.TeleBot(API_TOKEN)

try:
    bot.set_my_commands([
        BotCommand("start", "🚀 Start / Main Menu"),
        BotCommand("menu", "🎛 Open Menu")
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

# Episode Details
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
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Direct Payment App Link Button
    markup.add(InlineKeyboardButton("⚡ Pay ₹30 Now (GPay/PhonePe)", url=UPI_INTENT_LINK))
    
    # Admin Contact Button
    markup.add(InlineKeyboardButton("💬 Admin se Baat Karein", url=f"https://t.me/{ADMIN_USERNAME}"))
    
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
    
    bot.reply_to(
        message,
        text=thanks_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.reply_to(
        message, 
        "📷 Kripya payment karne ke baad apna **screenshot** yahan bhejiye taaki aapko episodes ka link mil sake!"
    )

if __name__ == "__main__":
    keep_alive()
    print("🤖 Bot successfully start ho raha hai... (Direct Payment Mode) 🚀")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
