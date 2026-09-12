import os
import json
import time
import threading
import urllib.parse
from flask import Flask, request
import telebot
import google.generativeai as genai
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuration
TOKEN = os.environ.get('BOT_TOKEN', '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AQ.A80RH6kVs-703IHNMAZ9Bc52mPsf7SluJFwZQ91cduTud2jKjw')

# Aapka Correct Numeric Channel ID
MAIN_CHANNEL_ID = -1004382767346 
ADMIN_ID = 6817248389

# Aapki Verified UPI ID
UPI_ID = "badmashromeo0007@okaxis"

# Bot ka Username (Strictly Bot chat mein bhejne ke liye)
BOT_USERNAME = "Romeo_pay_bot"

# Initialize Bot and Flask
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        gemini_model = None
else:
    gemini_model = None

SETTINGS_FILE = "/tmp/bot_settings.json"

def load_settings():
    default_settings = {
        "episodes": "3517–3526",
        "price": "70",
        "total_eps": "10",
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

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

@app.route('/')
def index():
    return "The Super Yoddha Bot is running live!"

# --- MARKUP ---
def get_payment_markup(is_channel=False):
    settings = load_settings()
    episodes = settings.get("episodes", "3517–3526")
    ep_text = f"Episode {episodes.split('–')[0]} To {episodes.split('–')[1] if '–' in episodes else episodes}"
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    
    if is_channel:
        # Yeh link user ko 100% channel se nikal kar seedha bot ki private chat me le jayega
        bot_deeplink = f"https://t.me/{BOT_USERNAME}?start=qr"
        markup.add(
            InlineKeyboardButton(ep_text, url=bot_deeplink),
            InlineKeyboardButton("📢 Join Main Channel", url="https://t.me/+gy8gewj0snllZThl")
        )
    else:
        markup.add(
            InlineKeyboardButton(ep_text, callback_data="show_qr"),
            InlineKeyboardButton("📢 Join Main Channel", url="https://t.me/+gy8gewj0snllZThl")
        )
    return markup

@bot.message_handler(commands=['setep'])
def set_episodes(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_ep = args[1]
        settings = load_settings()
        settings["episodes"] = new_ep
        save_settings(settings)
        bot.reply_to(message, f"✅ Episode range updated to: **{new_ep}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setep 3517–3526`", parse_mode="Markdown")

@bot.message_handler(commands=['setprice'])
def set_price(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_price = args[1].replace("₹", "").strip()
        settings = load_settings()
        settings["price"] = new_price
        save_settings(settings)
        bot.reply_to(message, f"✅ Price updated to: **₹{new_price}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setprice 70`", parse_mode="Markdown")

@bot.message_handler(commands=['setlink'])
def set_link(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_link = args[1]
        settings = load_settings()
        settings["access_link"] = new_link
        save_settings(settings)
        bot.reply_to(message, f"✅ Access Link updated successfully!", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setlink https://t.me/+8jC-...`", parse_mode="Markdown")

@bot.message_handler(content_types=['audio'])
def handle_audio_upload(message):
    if message.from_user.id != ADMIN_ID:
        return
    audio_file_id = message.audio.file_id
    bot.reply_to(message, f"✅ Audio received!\n\n**File ID:** `{audio_file_id}`", parse_mode="Markdown")

@bot.message_handler(commands=['sendchannel', 'broadcast'])
def send_to_main_channel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Aap admin nahi hain!")
        return
    
    settings = load_settings()
    
    welcome_text = (
        "🎧 **EPISODE PRICING** 🎧\n\n"
        f"📦 **{settings['episodes']}**\n\n"
        f"➡️ **10 Episodes — ₹{settings['price']}**\n\n"
        "⚡ **INSTANT DELIVERY** 🎁\n\n"
        "📩 **DM — [ROMEO_PAY_BOT](https://t.me/Romeo_pay_bot)** 🎉"
    )
    
    AUDIO_FILE_ID = "YAHAN_APNI_AUDIO_KA_FILE_ID_DAALEIN"
    
    try:
        if AUDIO_FILE_ID != "YAHAN_APNI_AUDIO_KA_FILE_ID_DAALEIN":
            bot.send_audio(
                MAIN_CHANNEL_ID, 
                audio=AUDIO_FILE_ID, 
                caption=welcome_text, 
                parse_mode="Markdown", 
                reply_markup=get_payment_markup(is_channel=True)
            )
        else:
            bot.send_message(
                MAIN_CHANNEL_ID, 
                welcome_text, 
                parse_mode="Markdown", 
                reply_markup=get_payment_markup(is_channel=True), 
                disable_web_page_preview=True
            )
        bot.reply_to(message, f"✅ Post successfully channel par bhej di gayi hai!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['start', 'menu', 'buy', 'qr'])
def send_welcome(message):
    settings = load_settings()
    
    # Agar user channel ke button se aaya hai (jaise ?start=qr), toh seedha QR code bhej do
    if len(message.text.split()) > 1 and message.text.split()[1] == "qr":
        send_qr_code_logic(message.chat.id, settings)
        return

    welcome_text = (
        "🎧 **EPISODE PRICING** 🎧\n\n"
        f"📦 **{settings['episodes']}**\n\n"
        f"➡️ **10 Episodes — ₹{settings['price']}**\n\n"
        "⚡ **INSTANT DELIVERY** 🎁\n\n"
        "📩 **DM — [ROMEO_PAY_BOT](https://t.me/Romeo_pay_bot)** 🎉"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=get_payment_markup(is_channel=False))

def send_qr_code_logic(chat_id, settings):
    price = settings.get("price", "70").replace("₹", "").strip()
    
    upi_string = f"upi://pay?pa={UPI_ID}&pn=TheSuperYoddha&am={price}&cu=INR"
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_string)}"
    
    qr_caption = (
        "⚡ **The Super Yoddha Payment QR Code** ⚡\n\n"
        f"• **UPI ID:** `{UPI_ID}`\n"
        f"• **Amount:** ₹{price}\n"
        f"• **Episodes:** {settings['episodes']}\n\n"
        "1. Is QR code ko kisi bhi UPI app se scan karke pay karein.\n"
        "2. Payment karne ke baad **screenshot yahin bot mein bhej dein**.\n"
        "3. Screenshot bhejte hi admin ke paas verification chali jayegi!"
    )
    
    try:
        bot.send_photo(chat_id, qr_image_url, caption=qr_caption, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, qr_caption, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "show_qr")
def callback_query(call):
    settings = load_settings()
    bot.answer_callback_query(call.id, "Yeh raha aapka payment QR code!")
    send_qr_code_logic(call.message.chat.id, settings)

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
    
    msg = bot.reply_to(message, "⏳ **Payment received!** Aapka payment verify kiya ja raha hai...\n⏱️ **Time remaining:** 60 seconds", parse_mode="Markdown")
    
    admin_markup = InlineKeyboardMarkup()
    admin_markup.row_width = 2
    admin_markup.add(
        InlineKeyboardButton("✅ Verify & Send Link", callback_data=f"verify_{user_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    )
    
    caption_for_admin = (
        f"🚨 **New Payment Screenshot Received!**\n\n"
        f"• **User Name:** {user_name}\n"
        f"• **Username:** {user_username}\n"
        f"• **User ID:** `{user_id}`\n\n"
        f"Kripya payment check karke button dabayein:"
    )
    
    try:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption_for_admin, parse_mode="Markdown", reply_markup=admin_markup)
    except Exception as e:
        print(f"Admin send error: {e}")
    
    def verification_timer(chat_id, message_id):
        time.sleep(60)
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="⏳ **Verification process mein thoda samay lag raha hai.**\n\nKripya thoda intezaar karein, jaise hi admin payment verify karenge, aapko turant link mil jayega! 🙏",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    threading.Thread(target=verification_timer, args=(message.chat.id, msg.message_id)).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify_") or call.data.startswith("reject_"))
def admin_action_handler(call):
    data = call.data.split("_")
    action = data[0]
    target_user_id = int(data[1])
    settings = load_settings()
    
    if action == "verify":
        try:
            success_text = (
                "🎉 **Payment Verified Successfully!** ✅\n\n"
                "Aapka payment approve ho gaya hai. Niche diye gaye link par click karke episodes join karein:\n\n"
                f"🔗 **Access Link:** {settings['access_link']}"
            )
            bot.send_message(target_user_id, success_text, parse_mode="Markdown", disable_web_page_preview=True)
            bot.answer_callback_query(call.id, "Payment verified & link sent to user!")
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n✅ **STATUS: VERIFIED & LINK SENT**", parse_mode="Markdown")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {e}")
            
    elif action == "reject":
        try:
            reject_text = "❌ Aapka payment screenshot reject kar diya gaya hai ya invalid hai. Kripya sahi screenshot dobara bhejen."
            bot.send_message(target_user_id, reject_text)
            bot.answer_callback_query(call.id, "Payment rejected!")
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n❌ **STATUS: REJECTED**", parse_mode="Markdown")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    settings = load_settings()
    
    welcome_text = (
        "🎧 **EPISODE PRICING** 🎧\n\n"
        f"📦 **{settings['episodes']}**\n\n"
        f"➡️ **10 Episodes — ₹{settings['price']}**\n\n"
        "⚡ **INSTANT DELIVERY** 🎁\n\n"
        "📩 **DM — [ROMEO_PAY_BOT](https://t.me/Romeo_pay_bot)** 🎉"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=get_payment_markup(is_channel=False))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
