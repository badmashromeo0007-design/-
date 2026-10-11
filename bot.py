import os
from flask import Flask, request
import telebot

# Bot Token directly set kar diya gaya hai
TOKEN = '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

ADMIN_ID = 6817248389
CHANNEL_ID = -1004382767346
UPI_ID = 'Badmashromeo0007@okaxis'


@app.route('/')
def home():
  return 'Bot is running successfully!'


# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
  markup = telebot.types.InlineKeyboardMarkup()
  # UPI Intent Link
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


# AlertBox Webhook Endpoint (Payment detect hone par yahan request aayegi)
@app.route('/alertbox-webhook', methods=['POST'])
def alertbox_webhook():
  try:
    data = request.json
    if not data:
      return 'No data', 400

    amount = data.get('amount', '0')
    sender = data.get('sender', 'Unknown')
    note = (
        data.get('note', '') or ''
    )  # User UPI note me apni Telegram ID daalega

    # Agar note me Telegram Chat ID di gayi hai
    if note and note.isdigit():
      target_chat_id = int(note)

      # Channel ka ek baar use hone wala invite link generate karein
      invite_link = bot.create_chat_invite_link(
          CHANNEL_ID, member_limit=1
      ).invite_link

      # User ko link bhejein
      bot.send_message(
          target_chat_id,
          f'✅ **Payment Successful! (₹{amount})**\n\n'
          f'Aapka payment receive ho gaya hai. Yahan aapka private channel link hai (Yeh link sirf ek baar use hoga):\n{invite_link}',
          parse_mode='Markdown',
      )
    else:
      # Agar note me ID nahi mili, toh Admin ko alert bhejein
      bot.send_message(
          ADMIN_ID,
          f'💰 **Naya Payment Aaya (Lekin ID match nahi hui)**\n\n'
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
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
    
