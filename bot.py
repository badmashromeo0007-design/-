import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN", "8831853256:AAFCFchvQVxwz9v_ACuhsL8ITSsNKpJ74nY")
bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
except Exception as e:
    print(f"Error removing webhook: {e}")

@bot.message_handler(func=lambda message: "Start / Menu" in message.text or message.text.startswith('/start'))
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn_ep = types.KeyboardButton("EP 3496 - 3503")
    markup.add(btn_ep)
    
    bot.reply_to(message, "🚀 **SUPER YODDHA — Audio Series**\n\nAapko kaun sa episode chahiye? Neeche diye gaye button par click karein:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "EP 3496 - 3503")
def handle_ep_menu(message):
    bot.reply_to(message, "Aapne **EP 3496 - 3503** select kiya hai. Yahan aapka audio series content open ho gaya hai!", parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot is starting polling...")
    bot.infinity_polling()
