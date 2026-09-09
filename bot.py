import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8831853256:AAESznbr52yif_PK47rXYzkTp5siAdloKAw"

bot = telebot.TeleBot(TOKEN)

PRICE_STANDARD = 50
PRICE_PREMIUM = 80
CHANNEL_ID = -1001234567890

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎬 Super Yoddha (₹50)", callback_data="buy_50"),
        InlineKeyboardButton("🔥 Special Episode (₹80)", callback_data="buy_80")
    )
    bot.send_message(
        message.chat.id, 
        "स्वागत है! 'Super Yoddha' ऑडियो सीरीज़ के एपिसोड्स खरीदने के लिए नीचे दिए गए विकल्प चुनें:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_payment_choice(call):
    amount = PRICE_STANDARD if call.data == "buy_50" else PRICE_PREMIUM
    bot.answer_callback_query(call.id, f"चुना गया मूल्य: ₹{amount}")
    bot.send_message(
        call.message.chat.id,
        f"कृपया ₹{amount} का भुगतान करें और स्क्रीनशॉट भेजें। भुगतान सत्यापित होने के बाद आपको चैनल का सिंगल-यूज़ लिंक मिल जाएगा।"
    )

if __name__ == "__main__":
    bot.infinity_polling()
