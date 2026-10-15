import os
import time
import telebot

TOKEN = '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU'
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6817248389
CHANNEL_ID = -1004382767346
UPI_ID = 'Badmashromeo0007@okaxis'


# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
  try:
    markup = telebot.types.InlineKeyboardMarkup()
    pay_btn = telebot.types.InlineKeyboardButton(
        '💳 Pay via UPI', url=f'upi://pay?pa={UPI_ID}&pn=Romeo&cu=INR'
    )
    markup.add(pay_btn)

    text = (
        'Paid Channel Access Bot\n\n'
        f'1. Diye gaye button se ya seedha is UPI ID par payment karein: {UPI_ID}\n'
        '2. Payment karte samay Note / Remarks mein apni Telegram ID zaroor likhein!\n'
        '3. Payment successful hote hi aapko channel ka link mil jayega.'
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)
  except Exception as e:
    print('Start error:', e)


print('Bot polling shuru ho rahi hai...')

# Webhook hata kar direct polling chalu karna
while True:
  try:
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
  except Exception as e:
    print('Polling error:', e)
    time.sleep(5)
