import os
import time
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

API_TOKEN = '8831853256:AAFOYW-K73PXAc8hHSJ1QvuVGBqudEU3fnY'
RENDER_URL = 'https://badmash-trp9.onrender.com' 

EPISODES_INVITE_LINK = 'https://t.me/+rViclcLru-0yYTI1'
ADMIN_USERNAME = "ROMEO_KERKETTA"
YOUR_UPI_ID = 'badmashromeo0007@okaxis'
PAYEE_NAME = "ROMEO"

app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN)

user_states = {}

try:
    bot.set_my_commands([
        BotCommand("start", "🚀 Choose Pack & Pay"),
        BotCommand("menu", "🎛 Open Menu")
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    user_states.pop(message.chat.id, None)
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔥 Buy Episodes Pack (₹150)", callback_data="pay_150"),
        InlineKeyboardButton("⚡ Buy Full Pack (₹180)", callback_data="pay_180"),
        InlineKeyboardButton("🤝 Mulbhav Karein (Budget Kam Hai?)", callback_data="start_bargain"),
        InlineKeyboardButton("💬 Admin se Sampark Karein", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    
    welcome_text = (
        f"🎧 **THE SUPER YODDHA EPISODES**\n\n"
        f"Standard Price: **₹180** | Special Pack: **₹150**\n"
        f"Agar budget kam hai, toh **'Mulbhav Karein'** button par click karke aap price kam kara sakte hain! 👇"
    )
    
    bot.send_message(
        chat_id=message.chat.id,
        text=welcome_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'start_bargain')
def start_bargain(call):
    # Step 1: Sabse pehle 150 ka offer dikhao
    user_states[call.message.chat.id] = {"step": "bargain_150"}
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Pay ₹150 (Yeh theek hai)", callback_data="accept_150"),
        InlineKeyboardButton("📉 Mere paas aur kam paise hain", callback_data="ask_120"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_custom")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            f"🤝 **Mulbhav (Step 1)**\n\n"
            f"Theek hai, hum aapke liye price kam kar dete hain.\n"
            f"Kya aap **₹150** mein yeh pack lena chahenge?"
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'ask_120')
def ask_120(call):
    # Step 2: Jab user bole paise kam hain, toh 120 do
    user_states[call.message.chat.id] = {"step": "bargain_120"}
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Pay ₹120 (Yeh theek hai)", callback_data="accept_120"),
        InlineKeyboardButton("📉 Mere paas isse bhi kam hain", callback_data="ask_100"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_custom")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            f"🤝 **Mulbhav (Step 2)**\n\n"
            f"Chaliye aapke liye price aur thoda kam kar dete hain.\n"
            f"Kya aap **₹120** mein maan jayenge?"
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'ask_100')
def ask_100(call):
    # Step 3: Aakhri limit 100
    user_states[call.message.chat.id] = {"step": "bargain_100"}
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Pay ₹100 (Final Offer)", callback_data="accept_100"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_custom")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            f"🤝 **Mulbhav (Final Step)**\n\n"
            f"Yeh hamari sabse aakhri aur minimum limit hai.\n"
            f"Kya aap **₹100** mein lena chahenge? (Isse kam mein dena sambhav nahi hai)."
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )

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
        InlineKeyboardButton("🔙 Menu Par Wapas Jayein", callback_data="cancel_custom")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            f"👍 Theek hai! Aapka **₹{amount}** ka deal fix ho gaya hai.\n\n"
            f"1️⃣ Neeche diye gaye **'Pay ₹{amount}'** button par click karke payment poori karein.\n"
            f"2️⃣ Payment ke baad **'Payment Ho Gayi? Link Lein'** dabayein."
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_custom')
def cancel_custom(call):
    user_states.pop(call.message.chat.id, None)
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
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            f"💰 **Aapne ₹{amount} ka pack select kiya hai.**\n\n"
            f"1️⃣ Upar diye gaye **'Pay ₹{amount}'** button par click karke payment poori karein.\n"
            f"2️⃣ Payment ke baad **'Payment Ho Gayi? Link Lein'** dabayein."
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def verify_payment_click(call):
    parts = call.data.split('_')
    amount = parts[1]
    
    success_text = (
        f"✨ **Payment Confirmed!** ✨\n"
        f"🎉 Aapka ₹{amount} ka pack successfully unlock ho gaya hai!\n\n"
        f"👇 Neeche diye gaye button se turant channel join karein:"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🚀 Join Episodes Channel", url=EPISODES_INVITE_LINK),
        InlineKeyboardButton("💬 Support", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=success_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

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
    return "Bot Webhook Server with Step-by-Step Bargain is running! 🚀"

if __name__ == "__main__":
    bot.remove_webhook()
    webhook_url = f"{RENDER_URL}/{API_TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"Webhook set to: {webhook_url}")
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    
