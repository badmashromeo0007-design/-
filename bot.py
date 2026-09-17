import os
import threading
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Aapki credentials aur IDs
TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389
UPI_ID = "badmashromeo0007@okaxis"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Flask route taaki UptimeRobot ping karke server ko active rakhe
@app.route('/')
def home():
    return "Bot is active and running!"

# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Pack 1 (₹50)", callback_data="pack_50"),
        InlineKeyboardButton("Pack 2 (₹150)", callback_data="pack_150")
    )
    welcome_text = (
        "👋 Welcome to Episode Bot!\n\n"
        "Niche diye gaye packs mein se apna pasandeeda pack select karein "
        "aur payment karke turant access payen:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Packs par click karne par UPI ID dikhane ka handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "pack_50":
        text = f"Aapne Pack 1 (₹50) chuna hai.\nKripya is UPI ID par payment karein:\n`{UPI_ID}`\n\nPayment karne ke baad screenshot yahan bhej dein."
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    elif call.data == "pack_150":
        text = f"Aapne Pack 2 (₹150) chuna hai.\nKripya is UPI ID par payment karein:\n`{UPI_ID}`\n\nPayment karne ke baad screenshot yahan bhej dein."
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

# Payment screenshot handle karne aur admin ko bhejne ka code (Bina parse error ke)
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    caption = f"New Payment Screenshot from user: {user_name} (ID: {user_id})"
    
    try:
        # Admin ke paas photo bina kisi formatting error ke bhejna
        bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=caption
        )
        bot.reply_to(message, "Aapka screenshot admin ke paas bhej diya gaya hai. Verification ke baad aapko access mil jayega.")
    except Exception as e:
        print(f"Error sending screenshot: {e}")
        bot.reply_to(message, "Screenshot bhejne mein kuch dikkat aayi. Kripya dobara koshish karein.")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flask server ko alag thread mein chalana taaki bot polling na ruke
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Bot polling start karna
    print("Bot is polling...")
    bot.infinity_polling()
    
