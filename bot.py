import os
import json
import time
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import google.generativeai as genai


API_TOKEN = '8831853256:AAFOYW-K73PXAc8hHSJ1QvuVGBqudEU3fnY'
GEMINI_API_KEY = 'AQ.Ab8RN6KJCiUJrMwS6JrsCkSP_Hfd9ZRH0wb_qoKrgZCX4MPSdg'  # Aapki Gemini API Key yahan set kar di gayi hai
RENDER_URL = 'https://badmash-trp9.onrender.com' 

# Links & Admin Configuration
MAIN_CHANNEL_LINK = 'https://t.me/+gy8gewj0snllZThl'
DEFAULT_EPISODE_LINK = 'https://t.me/+rViclcLru-0yYTI1'
BOT_PROFILE_LINK = 'https://t.me/TheSuperYoddhaBot'
ADMIN_USER_ID = 123456789  # Apna real Telegram User ID yahan daalein
ADMIN_USERNAME = "ROMEO_KERKETTA"
YOUR_UPI_ID = 'badmashromeo0007@okaxis'
PAYEE_NAME = "ROMEO"

app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

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
        BotCommand("start", "🚀 Choose Pack & Pay"),
        BotCommand("menu", "🎛 Open Menu"),
        BotCommand("setlink", "🔗 Set New Episode Link (Admin)"),
        BotCommand("getlink", "🔍 Check Current Episode Link (Admin)")
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
        bot.reply_to(message, "⚠️ Kripya link bhi dein.\nUsage: `/setlink https://t.me/...`", parse_mode="Markdown")
        return
    
    new_link = parts[1].strip()
    set_current_episode_link(new_link)
    bot.reply_to(message, f"✅ **Naya Episode Link Successfully Set Ho Gaya Hai!**\n\n🔗 `{new_link}`", parse_mode="Markdown")

@bot.message_handler(commands=['getlink'])
def get_episode_link_command(message):
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "⚠️ Yeh command sirf Admin ke liye hai!")
        return
    
    current_link = get_current_episode_link()
    bot.reply_to(message, f"🔗 **Current Active Episode Link:**\n{current_link}", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_USER_ID, content_types=['photo', 'video', 'document', 'audio'])
def forward_admin_media_to_channel(message):
    try:
        bot.copy_message(
            chat_id=MAIN_CHANNEL_LINK, 
            from_chat_id=message.chat.id, 
            message_id=message.message_id
        )
        bot.reply_to(message, "✅ Media successfully Main Channel par bhej diya gaya hai!")
    except Exception as e:
        bot.reply_to(message, f"❌ Channel par bhejte waqt error aaya:\n`{e}`", parse_mode="Markdown")

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    user_states.pop(message.chat.id, None)
    user_id_str = str(message.from_user.id)
    db = load_data()
    
    user_info = db.get(user_id_str, {"purchases": 0, "streak": 0, "last_date": ""})
    purchases = user_info.get("purchases", 0)
    streak = user_info.get("streak", 0)
    
    total_buyers = get_total_unique_buyers(db)
    global_offers_open = total_buyers >= 10
    user_knows_offer = global_offers_open and streak >= 6

    markup = InlineKeyboardMarkup(row_width=1)
    
    if user_knows_offer:
        markup.add(
            InlineKeyboardButton("🔥 Buy Episodes Pack (₹150)", callback_data="pay_150"),
            InlineKeyboardButton("⚡ Buy Full Pack (₹180)", callback_data="pay_180"),
            InlineKeyboardButton("🤝 Secret Mulbhav Karein", callback_data="start_bargain")
        )
        status_text = f"🌟 **Special Loyalty Status Active!** (Streak: {streak}/6 din)"
    else:
        markup.add(
            InlineKeyboardButton("⚡ Buy Episodes Pack (₹180)", callback_data="pay_180")
        )
        status_text = f"🎧 Apni pasand ke episodes turant prapt karein."
    
    markup.add(InlineKeyboardButton("📢 Join The Super Yoddha Main Channel", url=MAIN_CHANNEL_LINK))
    
    if purchases >= 5:
        markup.add(InlineKeyboardButton("💬 Admin se Sampark Karein", url=f"https://t.me/{ADMIN_USERNAME}"))
    
    welcome_text = (
        f"🎬 **THE SUPER YODDHA EPISODES**\n\n"
        f"{status_text}\n\n"
        f"Neeche diye gaye button par click karke payment karein aur instant access payen: 👇"
    )
    
    bot.send_message(
        chat_id=message.chat.id,
        text=welcome_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

# 🤖 Gemini AI Text Handler: Jab koi random text bhejega, AI smart reply dega
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_ai_chat(message):
    if message.from_user.id == ADMIN_USER_ID:
        bot.reply_to(message, "ℹ️ Link set karne ke liye `/setlink <link>` use karein, ya menu ke liye `/menu` bhejein.", parse_mode="Markdown")
        return
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"You are a helpful assistant for 'The Super Yoddha' audio series bot on Telegram. Reply nicely and briefly to this user message in Hinglish: {message.text}"
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        send_welcome(message)

@bot.callback_query_handler(func=lambda call: call.data == 'start_bargain')
def start_bargain(call):
    db = load_data()
    user_id_str = str(call.from_user.id)
    user_info = db.get(user_id_str, {})
    
    if get_total_unique_buyers(db) < 10 or user_info.get("streak", 0) < 6:
        bot.answer_callback_query(call.id, "⚠️ Yeh secret feature abhi aapke liye available nahi hai!", show_alert=True)
        return
        
    user_states[call.message.chat.id] = {"step": "bargain_150"}
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Pay ₹150 (Yeh theek hai)", callback_data="accept_150"),
        InlineKeyboardButton("📉 Mere paas aur kam paise hain", callback_data="ask_120"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_custom")
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🤝 **Secret Mulbhav (Step 1)**\n\nKya aap **₹150** mein yeh pack lena chahenge?",
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'ask_120')
def ask_120(call):
    user_states[call.message.chat.id] = {"step": "bargain_120"}
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Pay ₹120 (Yeh theek hai)", callback_data="accept_120"),
        InlineKeyboardButton("📉 Mere paas isse bhi kam hain", callback_data="ask_100"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_custom")
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🤝 **Secret Mulbhav (Step 2)**\n\nChaliye price aur thoda kam kar dete hain.\nKya aap **₹120** mein maan jayenge?",
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'ask_100')
def ask_100(call):
    user_states[call.message.chat.id] = {"step": "bargain_100"}
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Pay ₹100 (Final Offer)", callback_data="accept_100"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_custom")
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🤝 **Secret Mulbhav (Final Step)**\n\nYeh hamari sabse aakhri aur minimum limit hai.\nKya aap **₹100** mein lena chahenge?",
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: call.data in ['accept_150', 'accept_120', 'accept_100'])
def accept_bargain_amount(call):
    amount = call.data.split('_')[1]
    user_states.pop(call.message.chat.id, None)
    user_id = call.from_user.id
    unique_txn_id = f"SY_B_{user_id}_{int(time.time())}"
    
    upi_intent_url = (
        f"upi://pay?pa={YOUR_UPI_ID}&pn={PAYEE_NAME}"
        f"&am={amount}.00&cu=INR&tr={unique_txn_id}"
        f"&tn=SuperYoddha_Bargain_{amount}INR"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"💳 Pay ₹{amount} (Direct UPI App)", url=upi_intent_url),
        InlineKeyboardButton("🔄 Payment Ho Gayi? Link Lein", callback_data=f"verify_{amount}_{unique_txn_id}"),
        InlineKeyboardButton("🔙 Menu Par Jayein", callback_data="cancel_custom")
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"👍 Theek hai! Aapka **₹{amount}** ka deal fix ho gaya hai.\n\n1️⃣ Neeche diye gaye **'Pay ₹{amount}'** button par click karke payment poori karein.\n2️⃣ Payment ke baad **'Payment Ho Gayi? Link Lein'** dabayein.",
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_custom')
def cancel_custom(call):
    user_states.pop(call.message.chat.id, None)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_welcome(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def handle_payment_selection(call):
    amount = "150" if call.data == "pay_150" else "180"
    user_id = call.from_user.id
    unique_txn_id = f"SY_{user_id}_{int(time.time())}"
    
    upi_intent_url = (
        f"upi://pay?pa={YOUR_UPI_ID}&pn={PAYEE_NAME}"
        f"&am={amount}.00&cu=INR&tr={unique_txn_id}"
        f"&tn=SuperYoddha_{amount}INR"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"💳 Pay ₹{amount} (Direct UPI App)", url=upi_intent_url),
        InlineKeyboardButton("🔄 Payment Ho Gayi? Link Lein", callback_data=f"verify_{amount}_{unique_txn_id}")
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"💰 **Aapne ₹{amount} ka pack select kiya hai.**\n\n1️⃣ Upar diye gaye **'Pay ₹{amount}'** button par click karke payment poori karein.\n2️⃣ Payment ke baad **'Payment Ho Gayi? Link Lein'** dabayein.",
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def verify_payment_click(call):
    parts = call.data.split('_')
    amount = parts[1]
    
    user_id_str = str(call.from_user.id)
    db = load_data()
    
    current_date = time.strftime("%Y-%m-%d")
    user_info = db.get(user_id_str, {"purchases": 0, "streak": 0, "last_date": ""})
    
    last_date = user_info.get("last_date", "")
    streak = user_info.get("streak", 0)
    purchases = user_info.get("purchases", 0)
    
    if last_date != current_date:
        yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        if last_date == yesterday:
            streak += 1
        elif last_date == "":
            streak = 1
        else:
            streak = 1
            
        user_info["last_date"] = current_date
    
    purchases += 1
    user_info["purchases"] = purchases
    user_info["streak"] = streak
    db[user_id_str] = user_info
    save_data(db)
    
    active_episode_link = get_current_episode_link()
    total_buyers = get_total_unique_buyers(db)
    
    success_text = (
        f"✨ **Payment Confirmed!** ✨\n"
        f"🎉 Aapka ₹{amount} ka pack successfully unlock ho gaya hai!\n\n"
        f"🔥 Current Streak: **{streak} din** ho gaye hain.\n\n"
        f"👇 Neeche diye gaye button se **Aaj ka Episode** turant dekhein:"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("🎬 Aaj Ka Episode Dekhein (Turant Kholen)", url=active_episode_link))
    markup.add(InlineKeyboardButton("🤖 Bot Par Wapas Jayein", url=BOT_PROFILE_LINK))
    
    if total_buyers >= 10 and streak >= 6:
        success_text += "\n\n🎁 **Congratulations! Lagatar 6 din kharidari karne par 7vein din ka free episode reward link yeh raha:**"
        markup.add(InlineKeyboardButton("🎁 Claim Free Episode (Day 7 Reward)", url=active_episode_link))
        user_info["streak"] = 0 
        save_data(db)
        
    markup.add(InlineKeyboardButton("🔙 Main Menu Par Jayein", callback_data="cancel_custom"))
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=success_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception:
        pass

@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Forbidden", 403

@app.route('/')
def home():
    return "Bot with Gemini AI & Admin Panel is running! 🚀"

if __name__ == "__main__":
    bot.remove_webhook()
    webhook_url = f"{RENDER_URL}/{API_TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"Webhook set to: {webhook_url}")
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    
