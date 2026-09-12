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
MAIN_CHANNEL_ID = "@TheSuperYoddha" 
ADMIN_ID = 6817248389

# Aapki Verified UPI ID
UPI_ID = "badmashromeo0007@okaxis"

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
        "episodes": "EP 3517 - 3526",
        "price": "70",
        "prebook_price": "100",
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

# --- DYNAMIC UPI INTENT MARKUP ---
def get_payment_markup():
    settings = load_settings()
    p_price = settings.get("price", "70").replace("₹", "").strip()
    wb_price = settings.get("prebook_price", "100").replace("₹", "").strip()
    
    # UPI Intent URLs
    instant_upi_url = f"upi://pay?pa={UPI_ID}&pn=TheSuperYoddha&am={p_price}&cu=INR"
    prebook_upi_url = f"upi://pay?pa={UPI_ID}&pn=TheSuperYoddha&am={wb_price}&cu=INR"

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(f"⚡ Pay ₹{p_price} (Instant Episodes)", url=instant_upi_url),
        InlineKeyboardButton(f"🔥 Pay ₹{wb_price} (Pre-Booking)", url=prebook_upi_url),
        InlineKeyboardButton("📸 QR Code / Barcode Dekhein", callback_data="show_qr"),
        InlineKeyboardButton("📢 Join Main Channel", url="https://t.me/+gy8gewj0snllZThl")
    )
    return markup

def get_channel_post_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    bot_username = bot.get_me().username
    markup.add(
        InlineKeyboardButton("🗳️ Vote & Buy Now (DM)", url=f"https://t.me/{bot_username}")
    )
    return markup

# Admin Commands
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
        new_price = args[1].replace("₹", "").strip()
        settings = load_settings()
        settings["price"] = new_price
        save_settings(settings)
        bot.reply_to(message, f"✅ Price update ho gaya hai!\nNaya: **₹{new_price}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setprice 70`", parse_mode="Markdown")

@bot.message_handler(commands=['setprebookprice'])
def set_prebook_price(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_pre = args[1].replace("₹", "").strip()
        settings = load_settings()
        settings["prebook_price"] = new_pre
        save_settings(settings)
        bot.reply_to(message, f"✅ Pre-booking price update ho gaya hai!\nNaya: **₹{new_pre}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setprebookprice 100`", parse_mode="Markdown")

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

@bot.message_handler(commands=['sendpost'])
def send_post_to_channel(message):
    settings = load_settings()
    post_text = (
        f"✅ **EPISODES {settings['episodes']}** 🎉\n\n"
        f"💰 **PRICE — ₹{settings['price']}**\n\n"
        f"🎧 **TOTAL — 10 EPISODES** 💰\n\n"
        f"⚡ **INSTANT DELIVERY 🎁**"
    )
    try:
        bot.send_message(MAIN_CHANNEL_ID, post_text, parse_mode="Markdown", reply_markup=get_channel_post_markup())
        bot.reply_to(message, "✅ Post successfully channel par bhej di gayi hai!")
    except Exception as e:
        bot.reply_to(message, f"❌ Post bhejne mein error aayi: {e}")

@bot.message_handler(commands=['start', 'menu', 'buy', 'qr'])
def send_welcome(message):
    settings = load_settings()
    user_name = message.from_user.first_name
    welcome_text = (
        f"Namaste {user_name}! 🙏\n\n"
        "Welcome to **The Super Yoddha Bot**.\n\n"
        "🎬 **Available Now (Turant Milega ⚡):**\n"
        f"• Episodes: **{settings['episodes']}**\n"
        f"• Price: **₹{settings['price']}**\n\n"
        "🔥 **Pre-Booking (Advance Booking):**\n"
        f"• Price: **₹{settings['prebook_price']}**\n\n"
        "Payment karne ke liye neeche diye gaye button par click karein:"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=get_payment_markup(), disable_web_page_preview=True)

@bot.callback_query_handler(func=lambda call: call.data == "show_qr")
def callback_query(call):
    settings = load_settings()
    bot.answer_callback_query(call.id, "Yeh raha payment barcode!")
    qr_caption = (
        "⚡ **The Super Yoddha Payment QR Code**\n\n"
        f"• **Instant Episodes:** {settings['episodes']} (Price: ₹{settings['price']})\n"
        f"• **Pre-booking:** Price: ₹{settings['prebook_price']}\n\n"
        "1. Upar diye gaye direct button ya is QR code par pay karein.\n"
        "2. Payment karne ke baad **screenshot yahin bot mein bhej dein**.\n"
        "3. Screenshot bhejte hi admin ke paas verification chali jayegi!"
    )
    qr_image_url = "https://i.ibb.co/3ykB4rP/1000018603.png"
    try:
        bot.send_photo(call.message.chat.id, qr_image_url, caption=qr_caption, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, qr_caption, parse_mode="Markdown")

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
    user_text = message.text.lower()
    
    if "episode" in user_text or "chahiye" in user_text or "price" in user_text or "buy" in user_text or "prebook" in user_text or "qr" in user_text:
        reply_text = (
            "🎬 **The Super Yoddha Content Details:**\n\n"
            f"• **Available:** {settings['episodes']} — **₹{settings['price']}**\n"
            f"• **Pre-booking:** — **₹{settings['prebook_price']}**\n"
            "• **Delivery:** Turant Milega ⚡\n\n"
            "Payment karne ke liye neeche diye gaye button par click karein:"
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
        
        bot.reply_to(message, f"Aapko {settings['episodes']} (₹{settings['price']}) aur Pre-booking (₹{settings['prebook_price']}) mil jayenge! Payment ke liye button dabayein.", reply_markup=get_payment_markup())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
