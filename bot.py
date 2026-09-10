import os
from threading import Thread
from flask import Flask
import re
import telebot

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
API_TOKEN = '8831853256:AAHM8oOD0qVQs10uuCKLdieB9LrZ7vFTOOE'
STORAGE_CHANNEL_ID = '-1003621158878'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_queries(message):
    try:
        text = message.text
        if not text:
            return
        
        # 1. Naya / Available package (3503 se 3510) - ₹100 Fixed 🚀
        if "3503" in text or "3510" in text:
            response = (
                "🎧 **EPISODE 3503 → 3510** 🚀\n\n"
                "📦 **TOTAL — 8 EPISODES** 📚\n\n"
                "💰 **PRICE — ₹100 ONLY** 💵\n\n"
                "⚡ **TURANT MILEGA** 🔥\n\n"
                "📩 **DM:** @ROMEO_KERKETTA"
            )
            bot.reply_to(message, response, parse_mode="Markdown")
            return

        # 2. Purane episodes ke liye slabs aur calculation (1 se 3502) 📊
        numbers = re.findall(r'\d+', text)
        if numbers:
            count = int(numbers[0])
            
            # Agar maanga gaya episode available range (1 se 3502) ke andar hai:
            if 1 <= count <= 3502:
                rate_per_ep = 0
                
                # Pricing Slabs Rules:
                if count <= 100:
                    rate_per_ep = 5       # 1 se 100 tak: ₹5 per episode 💵
                elif count <= 300:
                    rate_per_ep = 3       # 101 se 300 tak: ₹3 per episode 💵
                elif count <= 500:
                    rate_per_ep = 2       # 301 se 500 tak: ₹2 per episode 💵
                else:
                    rate_per_ep = 1       # 500 se jyada: ₹1 per episode 💵
                    
                total_price = count * rate_per_ep
                
                response = (
                    f"📊 **EPISODE ORDER SUMMARY** 📋\n\n"
                    f"🔢 **Total Episodes:** {count} 📚\n"
                    f"🏷️ **Rate:** ₹{rate_per_ep} per episode 💵\n\n"
                    f"💰 **TOTAL PRICE — ₹{total_price}** 🔥\n\n"
                    f"🔒 *Content Secure hai (No Download/Forward)* 🛡️\n"
                    f"⚡ Payment ke baad episodes turant mil jayenge! 🚀\n\n"
                    f"📩 **Payment/Help ke liye DM karein:** @ROMEO_KERKETTA"
                )
                bot.reply_to(message, response, parse_mode="Markdown")
                return
            
            else:
                # Agar episode range (3502 se aage ya 0/negative) mein nahi hai:
                bot.reply_to(message, "❌ Yeh episode available nahi hai! 🚫 Kripya 1 se 3510 ke beech ka episode number bhejein.")
                return

        # 3. Agar text mein koi number nahi hai (General chat)
        ai_smart_response = (
           f"🤖 **AI Assistant:** Aapne kaha: *\"{text}\"* \n\n"
           f"👋 Namaste! Agar aapko audio series ke episodes chahiye, toh kripya episodes ki sankhya (jaise **50**, **200**, **500**) लिखकर भेजें! 🎧✨\n\n"
           f"📩 Kisi bhi sahayta ke liye DM karein: @ROMEO_KERKETTA"
        )
        bot.reply_to(message, ai_smart_response, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, "⚠️ Kuchh technical dikkat aayi hai, kripya dobara koshish karein! 🔄")

# --- 3. Main Execution with Flask Keep Alive ---
if __name__ == "__main__":
    keep_alive()  # Flask server background me start hoga taaki Render port error na de 🌐
    print("🤖 Bot successfully start ho raha hai... 🚀")
    bot.infinity_polling(skip_pending=True)
    
