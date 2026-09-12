import os
import json
import time
import threading
from flask import Flask, request
import telebot
import google.generativeai as genai
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuration
TOKEN = os.environ.get('BOT_TOKEN', '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AQ.A80RH6kVs-703IHNMAZ9Bc52mPsf7SluJFwZQ91cduTud2jKjw')

# Initialize Bot and Flask
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Configure Gemini AI Directly with your key
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Gemini Init Error: {e}")
        gemini_model = None
else:
    gemini_model = None

# Render Read-Only File System Bypass using /tmp for dynamic settings
SETTINGS_FILE = "/tmp/bot_settings.json"

def load_settings():
    default_settings = {
        "episodes": "EP 3517 - 3526",
        "price": "₹70",
        "prebook_ep": "EP 3527 - 3536",
        "prebook_price": "₹100",
        "access_link": "https://t.me/+8jC-7scof6diNzNl"
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return default_settings
    return default_settings

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Save error: {e}")

# Flask webhook Route to fix 404 Not Found Error
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

# Health Check Route
@app.route('/')
def index():
    return "The Super Yoddha Bot is running live!"

# Helper function for Markup
def get_payment_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("📸 QR Code / Barcode Dekhein", callback_data="show_qr"),
        InlineKeyboardButton("📢 Join Main Channel", url="https://t.me/+gy8gewj0snllZThl"),
        InlineKeyboardButton("💬 Admin ko Screenshot Bhejen", url="https://t.me/ROMEO_KERKETTA")
    )
    return markup

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['setep'])
def set_episodes(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_ep = args[1]
        settings = load_settings()
        settings["episodes"] = new_ep
        save_settings(settings)
        bot.reply_to(message, f"✅ Episode update ho gaya hai!\nNaya: **{new_ep}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setep EP 3517 - 3526`", parse_mode="Markdown")

@bot.message_handler(commands=['setprice'])
def set_price(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_price = args[1]
        settings = load_settings()
        settings["price"] = new_price
        save_settings(settings)
        bot.reply_to(message, f"✅ Price update ho gaya hai!\nNaya: **{new_price}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setprice ₹70`", parse_mode="Markdown")

@bot.message_handler(commands=['setprebook'])
def set_prebook(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_pre = args[1]
        settings = load_settings()
        settings["prebook_ep"] = new_pre
        save_settings(settings)
        bot.reply_to(message, f"✅ Pre-booking update ho gaya hai!\nNaya: **{new_pre}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setprebook EP 3527 - 3536`", parse_mode="Markdown")

@bot.message_handler(commands=['setlink'])
def set_link(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_link = args[1]
        settings = load_settings()
        settings["access_link"] = new_link
        save_settings(settings)
        bot.reply_to(message, f"✅ Access Link update ho gaya hai!\nNaya Link: `{new_link}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setlink https://t.me/+8jC-...`", parse_mode="Markdown")

# Telegram Command Handlers
@bot.message_handler(commands=['start', 'menu', 'buy', 'qr'])
def send_welcome(message):
    settings = load_settings()
    user_name = message.from_user.first_name
    welcome_text = (
        f"Namaste {user_name}! 🙏\n\n"
        "Welcome to **The Super Yoddha Bot**.\n\n"
        "🎬 **Available Now (Turant Milega ⚡):**\n"
        f"• Episodes: **{settings['episodes']}**\n"
        f"• Price: **{settings['price']}**\n\n"
        "🔥 **Pre-Booking (Advance Booking):**\n"
        f"• Episodes: **{settings['prebook_ep']}**\n"
        f"• Price: **{settings['prebook_price']}**\n\n"
        "Payment karne ke liye neeche diye gaye button par click karein:"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=get_payment_markup(), disable_web_page_preview=True)

# Handle Inline Button Clicks for QR
@bot.callback_query_handler(func=lambda call: call.data == "show_qr")
def callback_query(call):
    settings = load_settings()
    bot.answer_callback_query(call.id, "Yeh raha payment barcode!")
    qr_caption = (
        "⚡ **The Super Yoddha Payment QR Code**\n\n"
        f"• **Instant Episodes:** {settings['episodes']} (Price: {settings['price']})\n"
        f"• **Pre-booking Episodes:** {settings['prebook_ep']} (Price: {settings['prebook_price']})\n\n"
        "1. Is QR Code par GPay / PhonePe / Paytm se amount scan karke pay karein.\n"
        "2. Payment karne ke baad **payment ka screenshot yahin bot mein upload karein**.\n"
        "3. Screenshot bhejte hi verification timer shuru ho jayega!"
    )
    
    qr_image_url = "https://i.ibb.co/3ykB4rP/1000018603.png"
    
    try:
        bot.send_photo(call.message.chat.id, qr_image_url, caption=qr_caption, parse_mode="Markdown")
    except Exception as e:
        print(f"Photo send error: {e}")
        bot.send_message(call.message.chat.id, qr_caption, parse_mode="Markdown")

# Handle User Uploaded Screenshots / Photos for Verification
@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    
    # 1. User ko initial timer message bhejna
    msg = bot.reply_to(message, "⏳ **Payment received!** Aapka payment verify kiya ja raha hai...\n⏱️ **Time remaining:** 60 seconds", parse_mode="Markdown")
    
    # Background timer function
    def verification_timer(chat_id, message_id):
        time.sleep(60) # 1 minute wait
        try:
            # Agar 1 minute ke andar verify nahi hua (admin ne manual link nahi bheja)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="⏳ **Verification process mein thoda samay lag raha hai.**\n\nKripya thoda intezaar karein, jaise hi admin payment verify karenge, aapko turant episodes ka link mil jayega! 🙏",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Timer update error: {e}")

    # Start timer in background
    threading.Thread(target=verification_timer, args=(chat_id, msg.message_id)).start()

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    settings = load_settings()
    user_text = message.text.lower()
    
    if "episode" in user_text or "chahiye" in user_text or "price" in user_text or "buy" in user_text or "prebook" in user_text or "qr" in user_text:
        reply_text = (
            "🎬 **The Super Yoddha Content Details:**\n\n"
            f"• **Available:** {settings['episodes']} — **{settings['price']}**\n"
            f"• **Pre-booking:** {settings['prebook_ep']} — **{settings['prebook_price']}**\n"
            "• **Delivery:** Turant Milega ⚡\n\n"
            "Barcode dekhne ya payment karne ke liye neeche button dabayein:"
        )
        bot.reply_to(message, reply_text, parse_mode="Markdown", reply_markup=get_payment_markup(), disable_web_page_preview=True)
    else:
        if gemini_model:
            try:
                response = gemini_model.generate_content(message.text)
                if response and response.text:
                    bot.reply_to(message, response.text, reply_markup=get_payment_markup())
                    return
            except Exception as e:
                print(f"Gemini Error: {e}")
        
        bot.reply_to(message, f"Aapko {settings['episodes']} ({settings['price']}) aur Pre-booking {settings['prebook_ep']} ({settings['prebook_price']}) mil jayenge! Barcode dekhne ke liye button dabayein.", reply_markup=get_payment_markup())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
