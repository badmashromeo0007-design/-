import os
import json
import threading
import urllib.parse
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

# Configuration
TOKEN = os.environ.get('BOT_TOKEN', '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU')
MAIN_CHANNEL_ID = -1004382767346 
MAIN_CHANNEL_URL = "https://t.me/+gy8gewj0snllZThl"
UPI_ID = "badmashromeo0007@okaxis"
BOT_USERNAME = "Romeo_pay_bot"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

SETTINGS_FILE = "/tmp/bot_settings.json"

def load_settings():
    default_settings = {
        "episodes": "3517 TO 3526",
        "price": "70",
        "total_eps": "10",
        "access_link": "https://t.me/+8jC-7scof6diNzNl",
        "admin_id": 6817248389
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                if "admin_id" not in data:
                    data["admin_id"] = 6817248389
                return data
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

# Menu Markup: Top par Super Yoddha (Main Channel link), uske niche Episode button
def get_start_menu_markup():
    settings = load_settings()
    episodes = settings.get("episodes", "3517 TO 3526")
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("SUPER YODDHA (Main Channel)", url=MAIN_CHANNEL_URL),
        InlineKeyboardButton(f"EPISODE — {episodes}", callback_data="show_ep_details")
    )
    return markup

@bot.message_handler(commands=['setep'])
def set_episodes(message):
    settings = load_settings()
    settings["admin_id"] = message.from_user.id
    save_settings(settings)
    
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        settings["episodes"] = args[1]
        save_settings(settings)
        bot.reply_to(message, f"✅ Episode range updated to: **{args[1]}**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setep 3517 TO 3526`", parse_mode="Markdown")

@bot.message_handler(commands=['setprice'])
def set_price(message):
    settings = load_settings()
    settings["admin_id"] = message.from_user.id
    save_settings(settings)
    
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_price = args[1].replace("₹", "").replace("RS", "").strip()
        settings["price"] = new_price
        save_settings(settings)
        bot.reply_to(message, f"✅ Price updated to: **₹{new_price}RS**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setprice 70`", parse_mode="Markdown")

@bot.message_handler(commands=['setlink'])
def set_link(message):
    settings = load_settings()
    settings["admin_id"] = message.from_user.id
    save_settings(settings)
    
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_link = args[1].strip()
        settings["access_link"] = new_link
        save_settings(settings)
        bot.reply_to(message, f"✅ Access link updated successfully to:\n`{new_link}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Example: `/setlink https://t.me/+your_private_link`", parse_mode="Markdown")

@bot.message_handler(commands=['getlink'])
def get_link(message):
    settings = load_settings()
    current_link = settings.get("access_link", "Not set")
    bot.reply_to(message, f"🔗 **Current Access Link:**\n`{current_link}`", parse_mode="Markdown")

@bot.message_handler(commands=['sendchannel', 'broadcast'])
def send_to_main_channel(message):
    settings = load_settings()
    settings["admin_id"] = message.from_user.id
    save_settings(settings)
    
    channel_text = (
        "⚡ **SUPER YODDHA** ⚡\n\n"
        f"EPISODE — {settings['episodes']}\n\n"
        f"📦 TOTAL — {settings.get('total_eps', '10')} EPISODES\n"
        f"💰 PRICE — ₹{settings['price']}RS ✅\n\n"
        "⚡ INSTANT DELIVERY 🎁\n\n"
        f"📩 **Bot Link:** [ROMEO_PAY_BOT](https://t.me/{BOT_USERNAME})"
    )
    
    markup = InlineKeyboardMarkup()
    bot_deeplink = f"https://t.me/{BOT_USERNAME}?start=menu"
    markup.add(
        InlineKeyboardButton("SUPER YODDHA (Main Channel)", url=MAIN_CHANNEL_URL),
        InlineKeyboardButton(f"EPISODE — {settings['episodes']}", url=bot_deeplink)
    )
    
    try:
        bot.send_message(
            MAIN_CHANNEL_ID, 
            channel_text, 
            parse_mode="Markdown", 
            reply_markup=markup, 
            disable_web_page_preview=True
        )
        bot.reply_to(message, "✅ Post channel par bhej di gayi hai!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['start', 'menu', 'buy'])
def send_welcome(message):
    settings = load_settings()
    settings["admin_id"] = message.from_user.id
    save_settings(settings)

    if len(message.text.split()) > 1 and message.text.split()[1] == "menu":
        show_episode_details(message.chat.id, settings)
        return

    welcome_text = "⚡ **SUPER YODDHA** ⚡\n\nNeeche diye gaye buttons mein se select karein:"
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "👇 **Menu:**", reply_markup=get_start_menu_markup())

def show_episode_details(chat_id, settings):
    episodes = settings.get("episodes", "3517 TO 3526")
    price = settings.get("price", "70")
    total_eps = settings.get("total_eps", "10")
    
    detail_text = (
        "⚡ **SUPER YODDHA** ⚡\n\n"
        f"EPISODE — {episodes}\n\n"
        f"📦 TOTAL — {total_eps} EPISODES\n"
        f"💰 PRICE — ₹{price}RS ✅\n\n"
        "⚡ INSTANT DELIVERY"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Pay Now (Get QR Code)", callback_data="show_qr"))
    
    bot.send_message(chat_id, detail_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "show_ep_details")
def callback_ep_details(call):
    settings = load_settings()
    bot.answer_callback_query(call.id, "Loading Details...")
    show_episode_details(call.message.chat.id, settings)

def send_qr_code_logic(chat_id, settings):
    price = settings.get("price", "70").replace("₹", "").replace("RS", "").strip()
    upi_string = f"upi://pay?pa={UPI_ID}&pn=SuperYoddha&am={price}&cu=INR"
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_string)}"
    
    qr_caption = (
        "⚡ **SUPER YODDHA PAYMENT QR CODE** ⚡\n\n"
        f"• **UPI ID:** `{UPI_ID}`\n"
        f"• **Amount:** ₹{price}RS\n"
        f"• **Episodes:** {settings['episodes']}\n\n"
        "1. Is QR code ko scan karke payment karein.\n"
        "2. Payment karne ke baad **screenshot yahin bot mein bhej dein**."
    )
    try:
        bot.send_photo(chat_id, qr_image_url, caption=qr_caption, parse_mode="Markdown")
    except Exception:
        bot.send_message(chat_id, qr_caption, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "show_qr")
def callback_show_qr(call):
    settings = load_settings()
    bot.answer_callback_query(call.id, "Generating Barcode / QR...")
    send_qr_code_logic(call.message.chat.id, settings)

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    settings = load_settings()
    admin_id = settings.get("admin_id", message.from_user.id)
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    bot.reply_to(message, "⏳ **Payment received!** Verify kiya ja raha hai...", parse_mode="Markdown")
    
    admin_markup = InlineKeyboardMarkup()
    admin_markup.add(
        InlineKeyboardButton("✅ Verify & Send Link", callback_data=f"verify_{user_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    )
    
    try:
        bot.send_photo(admin_id, message.photo[-1].file_id, caption=f"🚨 New Payment from {user_name} (`{user_id}`)", parse_mode="Markdown", reply_markup=admin_markup)
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
    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Webhook reset error: {e}")
        
    print("Bot polling started in background...")
    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
