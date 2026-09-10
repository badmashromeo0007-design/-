import os
from threading import Thread
from flask import Flask
import re
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. Flask Web Server for Render Port Binding ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running successfully! 🚀🤖"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 2. Telegram Bot Configuration ---
API_TOKEN = '8831853256:AAGummjGke8vPpQ85EkWYTBzig5vh291XG8'
STORAGE_CHANNEL_ID = '-1003621158878'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_queries(message):
    try:
        text = message.text
        if not text:
            return
        
        # Range wale messages ko automatically calculate karne ke liye (Jaise 3496-3503 ya 3504-3510)
        range_match = re.search(r'(\d+)\s*-\s*(\d+)', text)
        if range_match:
            start_ep = int(range_match.group(1))
            end_ep = int(range_match.group(2))
            count = (end_ep - start_ep) + 1  
            
            if count > 0:
                # Agar 3504 se 3510 bheja hai toh chahein toh isko ₹100 fixed bhi rakh sakte hain
                if start_ep == 3504 and end_ep == 3510:
                    total_price = 100
                else:
                    # Baaki ranges ke liye rate calculation
                    rate_per_ep = 5
                    if count <= 100:
                        rate_per_ep = 5
                    elif count <= 300:
                        rate_per_ep = 3
                    elif count <= 500:
                        rate_per_ep = 2
                    else:
                        rate_per_ep = 1
                    total_price = count * rate_per_ep
                
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(f"⭐ Pay ₹{total_price} (EP {start_ep}-{end_ep})", callback_data="pay_stars"))
                
                response = (
                    f"📊 **EPISODE ORDER SUMMARY** 📋\n\n"
                    f"🔢 **Range:** {start_ep} → {end_ep} 📚\n"
                    f"📦 **Total Episodes:** {count} 📚\n\n"
                    f"💰 **TOTAL PRICE — ₹{total_price}** 🔥\n\n"
                    f"🔒 *Content Secure hai (No Download/Forward)* 🛡️\n"
                    f"⚡ Payment ke baad episodes turant mil jayenge! 🚀"
                )
                bot.reply_to(message, response, parse_mode="Markdown", reply_markup=markup)
                return

        # Simple numbers ke liye
        numbers = re.findall(r'\d+', text)
        if numbers:
            count = int(numbers[-1])
            rate_per_ep = 5 if count <= 100 else 3
            total_price = count * rate_per_ep
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f"⭐ Pay ₹{total_price} ({count} Episodes)", callback_data="pay_stars"))
            
            response = (
                f"📊 **EPISODE ORDER SUMMARY** 📋\n\n"
                f"🔢 **Total Episodes:** {count} 📚\n"
                f"💰 **TOTAL PRICE — ₹{total_price}** 🔥\n\n"
                f"⚡ Payment ke baad episodes turant mil jayenge! 🚀"
            )
            bot.reply_to(message, response, parse_mode="Markdown", reply_markup=markup)
            return

        # General chat
        ai_smart_response = (
           f"🤖 **AI Assistant:** Aapne kaha: *\"{text}\"* \n\n"
           f"👋 Namaste! Kripya episodes ki range (jaise **3504 - 3510**) लिखकर भेजें! 🎧✨"
        )
        bot.reply_to(message, ai_smart_response, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, "⚠️ Kuchh technical dikkat aayi hai, kripya dobara koshish karein! 🔄")

@bot.callback_query_handler(func=lambda call: call.data == "pay_stars")
def handle_star_click(call):
    text_message = (
        "⭐ **TELEGRAM STARS PAYMENT** 💳\n\n"
        "✅ Aapka request accept kar liya gaya hai!\n"
        "📩 **Admin DM:** @ROMEO_KERKETTA"
    )
    bot.answer_callback_query(call.id, "Processing your request...")
    bot.send_message(call.message.chat.id, text_message, parse_mode="Markdown")

# --- 3. Main Execution with Flask Keep Alive ---
if __name__ == "__main__":
    keep_alive()
    print("🤖 Bot successfully start ho raha hai... 🚀")
    bot.infinity_polling(skip_pending=True)
    
