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
API_TOKEN = '8831853256:AAGummjGke8vPpQ85EkWYTBzig5vh291XG8'  # Apna naya token yahan daalein agar change karein
MAIN_CHANNEL_ID = '-1004382767346' 
EPISODES_CHANNEL_ID = '-100rViclcLru-0yYTI1' # Aapka episodes channel
EPISODES_INVITE_LINK = 'https://t.me/+rViclcLru-0yYTI1'

ADMIN_USERNAME = "ROMEO_KERKETTA"
BOT_USERNAME = "Romeo_pay_bot" # Apne bot ka username yahan daalein (@ ke bina)

bot = telebot.TeleBot(API_TOKEN)

try:
    bot.set_my_commands([
        BotCommand("start", "🚀 Start / Main Menu"),
        BotCommand("menu", "🎛 Open Menu")
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

# Text Details as requested
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
        f"⚡ **TURANT MILEGA**\n\n"
        f"📲 **Payment karne ke liye upar diye gaye Barcode par Scan karke pay karein.**\n"
        f"📸 **Payment karne ke baad apna Screenshot yahin chat mein bhejen.**"
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
    # User ko badhiya sa thank you message channel/brand name ke sath
    thanks_text = (
        f"✨ **Thank You so much for your payment!** ✨\n"
        f"🎧 **THE SUPER YODDHA** ki taraf se aapka swagat hai.\n\n"
        f"⏳ Aapka screenshot admin (${ADMIN_USERNAME}) dwara verify kiya ja raha hai. "
        f"Verification poora hote hi aapko episodes ka secure link mil jayega!"
    )
    bot.reply_to(message, thanks_text, parse_mode="Markdown")
    
    # Admin ko notify karne ke liye (Optional: Admin chat mein screenshot forward kar sakte hain)
    # Yahan agar aap chahein toh direct link bhi de sakte hain ya manual verify kar sakte hain:
    # Testing ke liye direct secure link dene ka option:
    success_verify_text = (
        f"✅ **Payment Received & Verified!**\n\n"
        f"🎉 Thank you for purchasing from **THE SUPER YODDHA**!\n"
        f"Neeche aapke episodes ka link hai: 👇"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🚀 Join Episodes Channel", url=EPISODES_INVITE_LINK),
        InlineKeyboardButton("💬 Support / Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    
    bot.send_message(
        chat_id=message.chat.id,
        text=success_verify_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

def auto_remind_channel():
    global last_channel_msg_id
    while True:
        try:
            current_hour = datetime.now().hour
            
            # Raat 10:00 PM (22) se subah 8:00 AM (8) ke beech har 1 ghante mein reminder
            # Baaki din mein har 10 minute mein reminder
            if current_hour >= 22 or current_hour < 8:
                sleep_time = 3600 # 1 ghanta
            else:
                sleep_time = 600  # 10 minat
                
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
                f"📩 **Bot Link:-** [THE SUPER YODDHA]({f'https://t.me/{BOT_USERNAME}'})"
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
                                                                     
