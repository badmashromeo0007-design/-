import os
import json
import time
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import google.generativeai as genai

API_TOKEN = '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU'
GEMINI_API_KEY = 'AIzaSyA8KM6KJCIUJVMr5SJrstkQjHfd92Hnwb_qdrg2CX4MF5dg'
RENDER_URL = 'https://badmash-tr95.onrender.com'

# Links & Configuration
MAIN_CHANNEL_LINK = 'https://t.me/+gy0gavj0e112Th1'
DEFAULT_EPISODE_LINK = 'https://t.me/c/Viclctru-0YFT1i'
YOUR_UPI_ID = "badmashromeo0007@okaxis"
PAYEE_NAME = "ROMEO"

app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
ai_client = genai.GenerativeModel('gemini-1.5-flash')

DATA_FILE = "/tmp/user_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Save error: {e}")

def get_current_episode_link():
    db = load_data()
    global_stats = db.get("global_stats", {})
    return global_stats.get("current_episode_link", DEFAULT_EPISODE_LINK)

def set_current_episode_link(link):
    db = load_data()
    if "global_stats" not in db:
        db["global_stats"] = {}
    db["global_stats"]["current_episode_link"] = link
    save_data(db)

try:
    bot.set_my_commands([
        BotCommand("start", "🎁 Choose Pack & Pay"),
        BotCommand("menu", "📖 Open Menu"),
        BotCommand("setlink", "🔗 Set New Episode Link"),
        BotCommand("getlink", "🔗 Check Current Episode Link"),
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

@bot.message_handler(commands=['setlink'])
def set_episode_link_command(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, f"⚠️ Kripya link bhi daalein. Aapka User ID: `{message.from_user.id}`\nExample: `/setlink https://t.me/...`", parse_mode="Markdown")
        return
    
    new_link = parts[1].strip()
    set_current_episode_link(new_link)
    bot.reply_to(message, f"✅ Naya Episode Link successfully update ho gaya:\n{new_link}")

@bot.message_handler(commands=['getlink'])
def get_episode_link_command(message):
    current_link = get_current_episode_link()
    bot.reply_to(message, f"🔗 Current Episode Link:\n{current_link}\n\n(Aapka User ID: `{message.from_user.id}`)", parse_mode="Markdown")

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    db = load_data()
    if user_id not in db:
        db[user_id] = {"purchases": 0}
        save_data(db)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⚡ Buy Episodes Pack (₹180)", callback_data="choose_pack"))
    markup.add(InlineKeyboardButton("📢 Join The Super Yoddha Main Channel", url=MAIN_CHANNEL_LINK))
    
    welcome_text = (
        "🎬 **THE SUPER YODDHA EPISODES**\n\n"
        "🎧 Apni pasand ke episodes turant prapt karein.\n\n"
        "Neeche diye gaye button par click karke payment karein aur instant access payen: 👇"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.from_user.id)
    
    if call.data == "choose_pack":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⭐ Single Episode Pack (₹10)", callback_data="pack_10"))
        markup.add(InlineKeyboardButton("🚀 Mega Pack (₹180)", callback_data="pack_180"))
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_main"))
        bot.edit_message_text("📦 Apni pasand ka pack select karein:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "pack_10":
        upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn={PAYEE_NAME}&am=10.00&cu=INR&tn=SingleEpisode"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 Pay via UPI App", url=upi_url))
        markup.add(InlineKeyboardButton("✅ Payment Ho Gaya (Verify)", callback_data="verify_payment_10"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="choose_pack"))
        bot.edit_message_text(f"💳 **₹10 Payment**\n\nUPI ID: `{YOUR_UPI_ID}`\n\nPayment karne ke baad niche diye gaye 'Verify Payment' button par click karein.", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "pack_180":
        upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn={PAYEE_NAME}&am=180.00&cu=INR&tn=EpisodesPack"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 Pay via UPI App", url=upi_url))
        markup.add(InlineKeyboardButton("✅ Payment Ho Gaya (Verify)", callback_data="verify_payment_180"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="choose_pack"))
        bot.edit_message_text(f"💳 **₹180 Payment**\n\nUPI ID: `{YOUR_UPI_ID}`\n\nPayment karne ke baad niche diye gaye 'Verify Payment' button par click karein.", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("verify_payment_"):
        db = load_data()
        if user_id not in db:
            db[user_id] = {}
        db[user_id]["purchases"] = db[user_id].get("purchases", 0) + 1
        save_data(db)
        
        episode_link = get_current_episode_link()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎧 Watch Episode Now", url=episode_link))
        bot.edit_message_text("🎉 Payment Verified Successfully!\nAapka episode link niche hai:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back_main":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚡ Buy Episodes Pack (₹180)", callback_data="choose_pack"))
        markup.add(InlineKeyboardButton("📢 Join The Super Yoddha Main Channel", url=MAIN_CHANNEL_LINK))
        welcome_text = (
            "🎬 **THE SUPER YODDHA EPISODES**\n\n"
            "🎧 Apni pasand ke episodes turant prapt karein.\n\n"
            "Neeche diye gaye button par click karke payment karein aur instant access payen: 👇"
        )
        bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@app.route('/webhook', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/')
def index():
    return 'Bot is running live!', 200

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f'{RENDER_URL}/webhook')
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
