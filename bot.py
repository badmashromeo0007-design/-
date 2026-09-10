import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

API_TOKEN = '8831853256:AAFOYW-K73PXAc8hHSJ1QvuVGBqudEU3fnY'
RENDER_URL = 'https://badmash-7bhkr73f.onrender.com' 

EPISODES_INVITE_LINK = 'https://t.me/+rViclcLru-0yYTI1'
ADMIN_USERNAME = "ROMEO_KERKETTA"
YOUR_UPI_ID = 'badmashromeo0007@okaxis'
PAYMENT_AMOUNT = '₹180'

app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN)

try:
    bot.set_my_commands([
        BotCommand("start", "🚀 Start / Main Menu"),
        BotCommand("menu", "🎛 Open Menu")
    ])
except Exception as e:
    print(f"Menu commands error: {e}")

FULL_TITLE = "EPISODE 3510 → 3520"
TOTAL_EPISODES = "TOTAL — 10 EPISODES"

def get_start_text():
    return (
        f"🎧 **{FULL_TITLE}**\n\n"
        f"📦 **{TOTAL_EPISODES}**\n\n"
        f"💰 **PRICE — {PAYMENT_AMOUNT} ONLY**\n\n"
        f"⚡ **Payment Kaise Karein:**\n"
        f"Neeche diye gaye UPI ID par kisi bhi app (GPay / PhonePe / Paytm) se **{PAYMENT_AMOUNT}** send karein:\n\n"
        f"👉 UPI ID: `{YOUR_UPI_ID}`\n\n"
        f"📷 Payment karne ke baad **screenshot** yahin chat me bhejiye, aapko turant episodes ka link mil jayega!"
    )

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("💬 Admin se Sampark Karein", url=f"https://t.me/{ADMIN_USERNAME}"))
    
    bot.send_message(
        chat_id=message.chat.id,
        text=get_start_text(),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    thanks_text = (
        f"✨ **Payment Ka Screenshot Mil Gaya! Thanks!** ✨\n"
        f"🎧 **THE SUPER YODDHA** channel par aapka swagat hai!\n\n"
        f"🎉 Aapka payment verify ho gaya hai! Neeche aapke episodes ka secure link hai: 👇"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🚀 Join Episodes Channel", url=EPISODES_INVITE_LINK),
        InlineKeyboardButton("💬 Support / Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    
    bot.reply_to(message, text=thanks_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.reply_to(message, "📷 Kripya payment karne ke baad apna **screenshot** yahan bhejiye taaki aapko episodes ka link mil sake!")

# Flask Route for Telegram Webhook
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
    return "Bot Webhook Server is running! 🚀"

if __name__ == "__main__":
    bot.remove_webhook()
    # Webhook URL set karte waqt token ke sath slash ensure karna
    webhook_url = f"{RENDER_URL}/{API_TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"Webhook set to: {webhook_url}")
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    
