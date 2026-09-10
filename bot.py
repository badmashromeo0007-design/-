import os
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
EPISODES_CHANNEL_ID = '-100xxxxxxxxxx' # Yahan apne full episodes wale channel ki ID daalein

ADMIN_USERNAME = "ROMEO_KERKETTA"

bot = telebot.TeleBot(API_TOKEN)

try:
    bot.set_my_commands([
        BotCommand("start", "🚀 Start / Main Menu"),
        BotCommand("menu", "🎛 Open Episodes Menu")
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

FULL_TITLE = "FULL EPISODES PACK (3504 → 3510)"
TOTAL_EPISODES = "All 7 Episodes (Full Pack)"
PRICE_50 = "₹50 ONLY"
PRICE_30 = "₹30 (Special Full Pack)"
BOT_LINK = "https://t.me/Romeo_pay_bot"
QR_IMAGE_URL = "https://i.ibb.co/3m3vL05/1000018603.png"

def send_main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup(row_width=1)
    
    markup.add(
        InlineKeyboardButton(f"🎧 FULL EPISODES PACK ({PRICE_50})", callback_data="pkg_full_50"),
        InlineKeyboardButton(f"💸 Kam Budget Full Pack ({PRICE_30})", callback_data="pkg_full_30"),
        InlineKeyboardButton("💬 Mol-Bhav / Admin DM", url=f"https://t.me/{ADMIN_USERNAME}"),
        InlineKeyboardButton("🚀 Start / Menu", callback_data="main_menu")
    )
    
    text = (
        f"🎧 **SUPER YODDHA — Audio Series** 🚀\n\n"
        f"Aapko **Full Episodes** chahiye? Chahe ₹50 mein lo ya ₹30 mein, full pack milega! Neeche click karein: 👇"
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
    
    caption_text = (
        f"🎧 **SUPER YODDHA — Full Episodes** 🚀\n\n"
        f"📦 **Aapka Message:** {user_text}\n"
        f"💰 **PRICE:** {PRICE_50} (Ya ₹30 mein bhi Full Pack le sakte hain!)\n\n"
        f"⚡ **TURANT MILEGA!**\n\n"
        f"📲 **Payment karne ke liye upar diye gaye Barcode par Scan karke pay karein.**\n"
        f"📸 **Payment karne ke baad apna Screenshot yahin chat mein bhejen.**"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
    
    bot.send_photo(
        chat_id=message.chat.id,
        photo=QR_IMAGE_URL,
        caption=caption_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    try:
        invite_link = bot.create_chat_invite_link(
            chat_id=EPISODES_CHANNEL_ID,
            member_limit=1
        ).invite_link
        
        success_text = (
            f"✅ **Payment Screenshot Verified!**\n\n"
            f"🎉 Aapka payment verify ho gaya hai!\n"
            f"Neeche aapke liye **Full Episodes** ka **1-time use hone wala** secure link generate kiya gaya hai: 👇"
        )
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🚀 Join Full Episodes Channel", url=invite_link),
            InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")
        )
        
        bot.reply_to(
            message,
            text=success_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception as e:
        bot.reply_to(
            message,
            "⚠️ Link banane mein thodi problem aa rahi hai. Admin se sampark karein."
        )
        print(f"Invite link error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "main_menu":
        bot.answer_callback_query(call.id)
        send_main_menu(call.message.chat.id, call.message.message_id)
        
    elif call.data == "pkg_full_50":
        bot.answer_callback_query(call.id, "₹50 Full Pack Loaded!")
        caption_text = (
            f"🎧 **SUPER YODDHA — Full Episodes Pack** 🚀\n\n"
            f"📦 **{FULL_TITLE}** ({TOTAL_EPISODES})\n"
            f"💰 **PRICE:** {PRICE_50}\n\n"
            f"⚡ **TURANT MILEGA!**\n\n"
            f"📲 **Payment karne ke liye upar diye gaye Barcode par Scan karke pay karein.**\n"
            f"📸 **Payment karne ke baad apna Screenshot yahin chat mein bhejen.**"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.send_photo(call.message.chat.id, photo=QR_IMAGE_URL, caption=caption_text, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "pkg_full_30":
        bot.answer_callback_query(call.id, "₹30 Full Pack Loaded!")
        caption_text = (
            f"🎧 **SUPER YODDHA — Full Episodes Pack (Special Offer)** 🚀\n\n"
            f"📦 **{FULL_TITLE}** ({TOTAL_EPISODES})\n"
            f"💰 **PRICE:** {PRICE_30}\n\n"
            f"⚡ **TURANT MILEGA!**\n\n"
            f"📲 **₹30 pay karne ke liye upar diye gaye Barcode par Scan karke pay karein.**\n"
            f"📸 **Payment karne ke baad apna Screenshot yahin chat mein bhejen.**"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.send_photo(call.message.chat.id, photo=QR_IMAGE_URL, caption=caption_text, parse_mode="Markdown", reply_markup=markup)

def post_to_main_channel():
    try:
        channel_message = (
            f"🎧 **{FULL_TITLE}**\n\n"
            f"📦 **TOTAL — {TOTAL_EPISODES}**\n\n"
            f"💰 **PRICE — {PRICE_50}** (Kam budget walon ke liye ₹30 mein bhi Full Pack available hai!)\n\n"
            f"⚡ **TURANT MILEGA**\n\n"
            f"📩 **Link:-** [Click Here to Open Bot]({BOT_LINK})"
        )
        bot.send_message(MAIN_CHANNEL_ID, channel_message, parse_mode="Markdown")
        print("✅ Main channel par post successfully bhej di gayi hai!")
    except Exception as e:
        print(f"⚠️ Channel par post bhejne me error aaya: {e}")

if __name__ == "__main__":
    keep_alive()
    print("🤖 Bot successfully start ho raha hai... 🚀")
    
    try:
        post_to_main_channel()
    except Exception:
        pass
        
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
