import json
import os
from flask import Flask, request
import telebot
from telebot import types

TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389  # Aapki Admin ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

SETTINGS_FILE = "bot_settings.json"


def load_settings():
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
  return "Bot is running 24/7 via Webhook!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
  if request.headers.get("content-type") == "application/json":
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "", 200
  else:
    return "Forbidden", 403


@bot.message_handler(commands=["start", "menu"])
def send_menu(message):
  settings = load_settings()
  start_ep = settings["start_ep"]
  end_ep = settings["end_ep"]
  price = settings["price"]
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


# Episodes update karne ki command: /setep 3517 3526
@bot.message_handler(commands=["setep"])
def set_episodes(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap admin nahi hain!")
    return

  try:
    text = message.text.replace("/setep", "").strip()
    if "-" in text:
      parts = text.split("-")
    else:
      parts = text.split()

    start_ep = int(parts[0].strip())
    end_ep = int(parts[1].strip())

    settings = load_settings()
    settings["start_ep"] = start_ep
    settings["end_ep"] = end_ep
    save_settings(settings)

    total_eps = (end_ep - start_ep) + 1
    bot.reply_to(
        message,
        f"✅ Episodes Updated Successfully!\nRange: {start_ep} - {end_ep}\nTotal:"
        f" {total_eps} Episodes",
    )
  except Exception as e:
    bot.reply_to(
        message,
        "Galat format! Sahi tareeqa yeh hai:\n`/setep 3517 3526`",
        parse_mode="Markdown",
    )


# Price update karne ki command: /setprice 70
@bot.message_handler(commands=["setprice"])
def set_price(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap admin nahi hain!")
    return

  try:
    parts = message.text.split()
    price = int(parts[1])

    settings = load_settings()
    settings["price"] = price
    save_settings(settings)

    bot.reply_to(message, f"✅ Price Updated Successfully!\nPrice: ₹{price}RS")
  except Exception as e:
    bot.reply_to(
        message,
        "Galat format! Sahi tareeqa yeh hai:\n`/setprice 70`",
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

  bot.send_message(call.message.chat.id, caption, parse_mode="Markdown")


if __name__ == "__main__":
  RENDER_URL = os.environ.get(
      "RENDER_EXTERNAL_URL", "https://badmash-4k97.onrender.com"
  )
  bot.remove_webhook()
  bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")

  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
  
