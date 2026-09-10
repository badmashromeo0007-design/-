import os
import time
from datetime import datetime
from threading import Thread
from flask import Flask
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
API_TOKEN = '8831853256:AAGummjGke8vPpQ85EkWYTBzig5vh291XG8'
MAIN_CHANNEL_ID = '-1004382767346' 
EPISODES_INVITE_LINK = 'https://t.me/+rViclcLru-0yYTI1'

ADMIN_USERNAME = "ROMEO_KERKETTA"
BOT_USERNAME = "Romeo_pay_bot" 

bot = telebot.TeleBot(API_TOKEN)

try:
    bot.set_my_commands([
        BotCommand("start", "🚀 Start / Main Menu"),
        BotCommand("menu", "🎛 Open Menu")
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

# Episode & Payment Details
FULL_TITLE = "EPISODE 3503 → 3510"
TOTAL_EPISODES = "TOTAL — 8 EPISODES"
PRICE_TEXT = "PRICE — ₹30 ONLY"
QR_IMAGE_URL = "https://i.ibb.co/3m3vL05/1000018603.png"

last_channel_msg_id = None

def get_start_caption():
    return (
        f"🎧 **{FULL_TITLE}**\n\n"
        f"📦 **{TOTAL_EPISODES}**\n\n"
        f"💰 **{PRICE_TEXT}**\n\n"
        f"Payment karne ke baad screenshot bhejiye"
    )

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Admin se Baat Karein", url=f"https://t.me/{ADMIN_USERNAME}"))
    
    bot.send_photo(
        chat_id=message.chat.id,
        photo=QR_IMAGE_URL,
        caption=get_start_caption(),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    thanks_text = (
        f"✨ **Payment Kar Diya Hai! Iske Liye Dil Se Thanks!** ✨\n"
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

def auto_remind_channel():
    global last_channel_msg_id
    while True:
        try:
            current_hour = datetime.now().hour
            
            # Raat 10:00 PM (22) se subah 8:00 AM (8) ke beech har 1 ghante (3600 sec) me reminder
            # Baaki din mein har 10 minute (600 sec) me reminder
            if current_hour >= 22 or current_hour < 8:
                sleep_time = 3600 
            else:
                sleep_time = 600  
                
            if last_channel_msg_id:
                try:
                    bot.delete_message(MAIN_CHANNEL_ID, last_channel_msg_id)
                except Exception as e:
                    print(f"Purana message delete karne mein error: {e}")

            channel_message = (
                f"🎧 **{FULL_TITLE}**\n\n"
                f"📦 **{TOTAL_EPISODES}**\n\n"
                f"💰 **{PRICE_TEXT}**\n\n"
                f"⚡ **TURANT MILEGA**\n\n"
                f"📩 **DM —** [THE SUPER YODDHA Bot]({f'https://t.me/{BOT_USERNAME}'})"
            )
            sent_msg = bot.send_message(MAIN_CHANNEL_ID, channel_message, parse_mode="Markdown")
            last_channel_msg_id = sent_msg.message_id
            print("✅ Main channel par reminder post bhej diya gaya hai!")
            
            time.sleep(sleep_time)
        except Exception as e:
            print(f"⚠️ Channel reminder error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    keep_alive()
    print("🤖 Bot successfully start ho raha hai... 🚀")
    
    channel_thread = Thread(target=auto_remind_channel)
    channel_thread.daemon = True
    channel_thread.start()
    
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
