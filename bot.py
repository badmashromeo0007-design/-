import os
import json
import threading
import urllib.parse
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuration
TOKEN = os.environ.get('BOT_TOKEN', '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU')
ADMIN_ID = 6817248389
MAIN_CHANNEL_ID = -1004382767346 
UPI_ID = "badmashromeo0007@okaxis"
BOT_USERNAME = "Romeo_pay_bot"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

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

@app.route('/')
def index():
    return "The Super Yoddha Bot is running live!"

def get_payment_markup(is_channel=False):
    settings = load_settings()
    episodes = settings.get("episodes", "3517–3526")
    ep_text = f"Episode {episodes.split('–')[0]} To {episodes.split('–')[1] if '–' in episodes else episodes}"
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    
    if is_channel:
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
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        settings = load_settings()
        settings["episodes"] = args[1]
        save_settings(settings)
        bot.reply_to(message, f"✅ Episode range updated to: **{args[1]}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setep 3517–3526`", parse_mode="Markdown")

@bot.message_handler(commands=['setprice'])
def set_price(message):
    if message.from_user.id != ADMIN_ID:
        return
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
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_link = args[1].strip()
        settings = load_settings()
        settings["access_link"] = new_link
        save_settings(settings)
        bot.reply_to(message, f"✅ Access link updated successfully to:\n`{new_link}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setlink https://t.me/+your_private_link`", parse_mode="Markdown")

@bot.message_handler(commands=['getlink'])
def get_link(message):
    if message.from_user.id != ADMIN_ID:
        return
    settings = load_settings()
    current_link = settings.get("access_link", "Not set")
    bot.reply_to(message, f"🔗 **Current Access Link:**\n`{current_link}`", parse_mode="Markdown")

@bot.message_handler(commands=['sendchannel', 'broadcast'])
def send_to_main_channel(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    settings = load_settings()
    welcome_text = (
        "🎧 **EPISODE PRICING** 🎧\n\n"
        f"📦 **{settings['episodes']}**\n\n"
        f"➡️ **10 Episodes — ₹{settings['price']}**\n\n"
        "⚡ **INSTANT DELIVERY** 🎁\n\n"
        "📩 **DM — [ROMEO_PAY_BOT](https://t.me/Romeo_pay_bot)** 🎉"
    )
    
    try:
        bot.send_message(
            MAIN_CHANNEL_ID, 
            welcome_text, 
            parse_mode="Markdown", 
            reply_markup=get_payment_markup(is_channel=True), 
            disable_web_page_preview=True
        )
        bot.reply_to(message, "✅ Post channel par bhej di gayi hai!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['start', 'menu', 'buy', 'qr'])
def send_welcome(message):
    settings = load_settings()
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
        "2. Payment karne ke baad **screenshot yahin bot mein bhej dein**."
    )
    try:
        bot.send_photo(chat_id, qr_image_url, caption=qr_caption, parse_mode="Markdown")
    except Exception:
        bot.send_message(chat_id, qr_caption, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "show_qr")
def callback_query(call):
    settings = load_settings()
    bot.answer_callback_query(call.id, "QR Code:")
    send_qr_code_logic(call.message.chat.id, settings)

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    bot.reply_to(message, "⏳ **Payment received!** Verify kiya ja raha hai...", parse_mode="Markdown")
    
    admin_markup = InlineKeyboardMarkup()
    admin_markup.add(
        InlineKeyboardButton("✅ Verify & Send Link", callback_data=f"verify_{user_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    )
    
    try:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🚨 New Payment from {user_name} (`{user_id}`)", parse_mode="Markdown", reply_markup=admin_markup)
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify_") or call.data.startswith("reject_"))
def admin_action_handler(call):
    data = call.data.split("_")
    action = data[0]
    target_user_id = int(data[1])
    settings = load_settings()
    
    if action == "verify":
        try:
            bot.send_message(target_user_id, f"🎉 **Payment Verified!**\n\nLink: {settings['access_link']}", parse_mode="Markdown")
            bot.answer_callback_query(call.id, "Verified!")
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n✅ **VERIFIED**", parse_mode="Markdown")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {e}")
    elif action == "reject":
        try:
            bot.send_message(target_user_id, "❌ Payment rejected.")
            bot.answer_callback_query(call.id, "Rejected!")
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n❌ **REJECTED**", parse_mode="Markdown")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {e}")

def run_bot():
    bot.remove_webhook()
    print("Bot polling started in background...")
    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
