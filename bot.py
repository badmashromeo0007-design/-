import json
import os
from flask import Flask
import telebot
from telebot import types

# Configurations
TOKEN = "YOUR_BOT_TOKEN"  # Apna bot token yahan daalein
ADMIN_ID = 6817248389  # Aapki Admin ID
CHANNEL_USERNAME = "@SUPER_YODDA"  # Main Channel

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Settings file jo episodes aur price ko yaad rakhegi
SETTINGS_FILE = "bot_settings.json"


def load_settings():
  # Default settings agar file na ho
  default_data = {
      "start_ep": 3527,
      "end_ep": 3533,
      "price": 100,
      "upi_id": "badmashromeo0007@okaxis",
  }
  if os.path.exists(SETTINGS_FILE):
    try:
      with open(SETTINGS_FILE, "r") as f:
        return json.load(f)
    except:
      return default_data
  return default_data


def save_settings(data):
  with open(SETTINGS_FILE, "w") as f:
    json.dump(data, f)


@app.route("/")
def home():
  return "Bot is running 24/7!"


@bot.message_handler(commands=["start", "menu"])
def send_menu(message):
  settings = load_settings()
  start_ep = settings["start_ep"]
  end_ep = settings["end_ep"]
  price = settings["price"]

  # Automatic calculation: Total episodes khud calculate ho jayenge!
  total_eps = (end_ep - start_ep) + 1

  text = (
      f"⚡ **SUPER YODDA** ⚡\n\n"
      f"📺 **EPISODE – {start_ep} - {end_ep}**\n\n"
      f"📦 **TOTAL – {total_eps} EPISODES**\n"
      f"💰 **PRICE – ₹{price}RS** ✅\n\n"
      f"⚡ **INSTANT DELIVERY**"
  )

  markup = types.InlineKeyboardMarkup()
  btn_pay = types.InlineKeyboardButton(
      "💳 Pay Now (Get QR Code)", callback_data="get_qr"
  )
  markup.add(btn_pay)

  bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")


# Admin command episodes change karne ke liye: /set 3534 3540 100
@bot.message_handler(commands=["set"])
def update_episodes(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap admin nahi hain!")
    return

  try:
    parts = message.text.split()
    start_ep = int(parts[1])
    end_ep = int(parts[2])
    price = int(parts[3])

    settings = load_settings()
    settings["start_ep"] = start_ep
    settings["end_ep"] = end_ep
    settings["price"] = price
    save_settings(settings)

    total_eps = (end_ep - start_ep) + 1
    bot.reply_to(
        message,
        f"✅ Success! Updated:\nEpisodes: {start_ep}-{end_ep}"
        f" ({total_eps} Episodes)\nPrice: ₹{price}",
    )
  except Exception as e:
    bot.reply_to(
        message,
        "Galat format! Sahi tareeqa yeh hai:\n`/set 3527 3533 100`",
        parse_mode="Markdown",
    )


@bot.callback_query_handler(func=lambda call: call.data == "get_qr")
def qr_handler(call):
  settings = load_settings()
  start_ep = settings["start_ep"]
  end_ep = settings["end_ep"]
  price = settings["price"]
  upi = settings["upi_id"]

  caption = (
      f"⚡ **SUPER YODDA PAYMENT QR CODE** ⚡\n\n"
      f"• UPI ID: `{upi}`\n"
      f"• Amount: ₹{price}RS\n"
      f"• Episodes: {start_ep} TO {end_ep}\n\n"
      f"1. Is QR code ko scan karke payment karein.\n"
      f"2. Payment karne ke baad screenshot yahin bot mein bhej dein."
  )

  # Yahan aap apni QR code image ka file_id ya URL daal sakte hain
  bot.send_message(
      call.message.chat.id, caption, parse_mode="Markdown"
  )  # Yahan photo bhi bhej sakte hain


if __name__ == "__main__":
  import threading

  # Flask server background mein chalane ke liye taaki Render / UptimeRobot ping kar sake
  def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

  threading.Thread(target=run_flask).start()

  # Bot polling start
  bot.infinity_polling()
    
