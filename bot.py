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

# Links & Admin Configuration
MAIN_CHANNEL_LINK = 'https://t.me/+gy0gavj0e112Th1'
DEFAULT_EPISODE_LINK = 'https://t.me/c/Viclctru-0YFT1i'
BOT_PROFILE_LINK = 'https://t.me/TheSuperYoddhabot'
ADMIN_USER_ID = 123456789  # Apna real Telegram User ID yahan daalein
ADMIN_USERNAME = "ROMEO_KERNKETA"
YOUR_UPI_ID = "badmashromeo0007@okaxis"
PAYEE_NAME = "ROMEO"

app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
ai_client = genai.GenerativeModel('gemini-1.5-flash')

user_states = {}
DATA_FILE = "user_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

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

def get_total_unique_buyers(db):
    buyers_count = 0
    for uid, info in db.items():
        if uid != "global_stats" and info.get("purchases", 0) > 0:
            buyers_count += 1
    return buyers_count

try:
    bot.set_my_commands([
        BotCommand("start", "🎁 Choose Pack & Pay"),
        BotCommand("menu", "📖 Open Menu"),
        BotCommand("setlink", "🔗 Set New Episode Link (Admin)"),
        BotCommand("getlink", "🔗 Check Current Episode Link (Admin)"),
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

@bot.message_handler(commands=['setlink'])
def set_episode_link_command(message):
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "⚠️ Yeh command sirf Admin ke liye hai!")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Kripya link bhi daalein. Example: `/setlink https://t.me/...`")
        return
    
    new_link = parts[1].strip()
    set_current_episode_link(new_link)
    bot.reply_to(message, f"✅ Naya Episode Link successfully update ho gaya:\n{new_link}")

@bot.message_handler(commands=['getlink'])
def get_episode_link_command(message):
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "⚠️ Yeh command sirf Admin ke liye hai!")
        return
    current_link = get_current_episode_link()
    bot.reply_to(message, f"🔗 Current Episode Link:\n{current_link}")

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    db = load_data()
    if user_id not in db:
        db[user_id] = {"purchases": 0}
        save_data(db)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 Choose Pack & Pay", callback_data="choose_pack"))
    markup.add(InlineKeyboardButton("📢 Join Main Channel", url=MAIN_CHANNEL_LINK))
    
    welcome_text = (
        "👋 Welcome to Super Yoddha Audio Series Bot!\n\n"
        "Yahan aapko milenge saare latest episodes. Niche diye gaye button par click karke packs dekhein aur pay karein."
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.from_user.id)
    
    if call.data == "choose_pack":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⭐ Single Episode Pack (₹10)", callback_data="pack_10"))
        markup.add(InlineKeyboardButton("🚀 Mega Pack (₹120)", callback_data="pack_120"))
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_main"))
        bot.edit_message_text("📦 Apni pasand ka pack select karein:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "pack_10":
        upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn={PAYEE_NAME}&am=10.00&cu=INR&tn=SingleEpisode"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 Pay via UPI App", url=upi_url))
        markup.add(InlineKeyboardButton("✅ Payment Ho Gaya (Verify)", callback_data="verify_payment_10"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="choose_pack"))
        bot.edit_message_text(f"💳 **₹10 Payment**\n\nUPI ID: `{YOUR_UPI_ID}`\n\nPayment karne ke baad niche diye gaye 'Verify Payment' button par click karein.", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "pack_120":
        upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn={PAYEE_NAME}&am=120.00&cu=INR&tn=MegaPack"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 Pay via UPI App", url=upi_url))
        markup.add(InlineKeyboardButton("✅ Payment Ho Gaya (Verify)", callback_data="verify_payment_120"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="choose_pack"))
        bot.edit_message_text(f"💳 **₹120 Payment**\n\nUPI ID: `{YOUR_UPI_ID}`\n\nPayment karne ke baad niche diye gaye 'Verify Payment' button par click karein.", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

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
        markup.add(InlineKeyboardButton("🎁 Choose Pack & Pay", callback_data="choose_pack"))
        markup.add(InlineKeyboardButton("📢 Join Main Channel", url=MAIN_CHANNEL_LINK))
        bot.edit_message_text("👋 Welcome back to main menu!", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    try:
        response = ai_client.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Maaf kijiye, abhi AI response generate karne mein kuch dikkat aa rahi hai.")

@app.route(f'/{API_TOKEN}', methods=['POST'])
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
    bot.set_webhook(url=f'{RENDER_URL}/{API_TOKEN}')
    app.run(host="0.0.0.0", port=10000)
    
