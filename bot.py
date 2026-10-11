import os
from flask import Flask, request
import telebot

TOKEN = '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

ADMIN_ID = 6817248389
CHANNEL_ID = -1004382767346
UPI_ID = 'Badmashromeo0007@okaxis'
RENDER_URL = 'https://badmash-4k97.onrender.com'


@app.route('/')
def home():
  return (
      'Bot is running successfully! Webhook set karne ke liye browser mein'
      ' /set_webhook kholein.'
  )


# Ek click par Telegram webhook set karne ka rasta
@app.route('/set_webhook')
def set_webhook():
  try:
    webhook_url = f'{RENDER_URL}/webhook'
    bot.remove_webhook()
    s = bot.set_webhook(url=webhook_url)
    if s:
      return f'✅ Webhook successfully set to: {webhook_url}'
    else:
      return '❌ Webhook setup failed!', 400
  except Exception as e:
    return f'Error: {str(e)}', 500


# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
  markup = telebot.types.InlineKeyboardMarkup()
  pay_btn = telebot.types.InlineKeyboardButton(
      '💳 Pay via UPI', url=f'upi://pay?pa={UPI_ID}&pn=Romeo&cu=INR'
  )
  markup.add(pay_btn)

  text = (
      '🚀 **Paid Channel Access Bot**\n\n'
      f'1️⃣ Diye gaye button se ya seedha is UPI ID par payment karein: `{UPI_ID}`\n'
      '2️⃣ Payment karte samay **Note / Remarks** mein apni Telegram ID zaroor likhein, taaki system aapko pehchan sake!\n'
      '3️⃣ Payment successful hote hi aapko channel ka link automatic mil jayega.'
  )
  bot.send_message(
      message.chat.id, text, parse_mode='Markdown', reply_markup=markup
  )


# AlertBox Webhook Endpoint
@app.route('/alertbox-webhook', methods=['POST'])
def alertbox_webhook():
  try:
    data = request.json
    if not data:
      return 'No data', 400

    amount = data.get('amount', '0')
    sender = data.get('sender', 'Unknown')
    note = data.get('note', '') or ''

    if note and note.isdigit():
      target_chat_id = int(note)
      invite_link = bot.create_chat_invite_link(
          CHANNEL_ID, member_limit=1
      ).invite_link
      bot.send_message(
          target_chat_id,
          f'✅ **Payment Successful! (₹{amount})**\n\n'
          f'Aapka payment receive ho gaya hai. Yahan aapka private channel link hai:\n{invite_link}',
          parse_mode='Markdown',
      )
    else:
      bot.send_message(
          ADMIN_ID,
          f'💰 **Naya Payment Aaya (ID match nahi hui)**\n\n'
          f'Amount: ₹{amount}\nSender: {sender}\nNote: {note}',
      )

    return 'OK', 200
  except Exception as e:
    print('Error:', e)
    return 'Error', 500


# Telegram Webhook Endpoint
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
  json_string = request.get_data().decode('utf-8')
  update = telebot.types.Update.de_json(json_string)
  bot.process_new_updates([update])
  return '!', 200


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
