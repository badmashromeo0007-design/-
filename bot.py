import re
import telebot

# [1] BotFather se mila hua apna asli API Token yahan dalein:
API_TOKEN = '8831853256:AAFCFchvQVxwz9v_ACuhsL8ITSsNKpJ74nY'

# [2] Aapke private channel ki numeric ID:
STORAGE_CHANNEL_ID = '-1004492110524'

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

        # 3. AI-Powered Smart Fallback for general chats/questions 🤖✨
        ai_smart_response = (
           f"🤖 **AI Assistant:** Aapne kaha: *\"{text}\"* \n\n"
           f"👋 Namaste! Agar aapko audio series ke episodes chahiye, toh kripya episodes ki sankhya (jaise **50**, **200**, **500**) लिखकर भेजें ताकि सही दाम और डिस्काउंट स्लैब का पता चल सके! 🎧✨\n\n"
           f"📩 Kisi bhi sahayta ke liye DM karein: @ROMEO_KERKETTA"
        )
        bot.reply_to(message, ai_smart_response, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, "⚠️ Kuchh technical dikkat aayi hai, kripya dobara koshish karein! 🔄")

print("🤖 AI-Integrated Telegram Bot successfully start ho raha hai... 🚀")
bot.infinity_polling(skip_pending=True)
