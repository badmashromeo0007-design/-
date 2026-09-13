import json
import os
import sqlite3
from flask import Flask, request
import telebot
from telebot import types

TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389  # Aapki Admin ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

SETTINGS_FILE = "bot_settings.json"
DB_FILE = "bot_database.db"


# Database Initialize karne ke liye
def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      """CREATE TABLE IF NOT EXISTS buyers (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
  )
  conn.commit()
  conn.close()


init_db()


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
  return "Bot is running 24/7 via Webhook with Auto-Approval System!"


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

  # Optional Audio Preview
  try:
    audio_file_path = "preview.mp3"
    if os.path.exists(audio_file_path):
      with open(audio_file_path, "rb") as audio:
        bot.send_audio(
            message.chat.id,
            audio,
            caption="🎧 **Super Yoddha Audio Preview**",
            parse_mode="Markdown",
        )
  except Exception as e:
    pass

  # Aapka exact design format
  text = (
      f"⚡ **SUPER YODDA** ⚡\n\n"
      f"📺 **EPISODE – {start_ep} - {end_ep}**\n\n"
      f"📦 **TOTAL – {total_eps} EPISODES**\n\n"
      f"💰 **PRICE – ₹{price}RS** ✅\n\n"
      f"⚡ **INSTANT DELIVERY**"
  )

  markup = types.InlineKeyboardMarkup()
  btn_pay = types.InlineKeyboardButton(
      "💳 Pay Now (Get QR Code)", callback_data="get_qr"
  )
  markup.add(btn_pay)

  bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")


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
        "Galat format! Sahi tareeqa yeh hai:\n`/setep 3527 3533`",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["setprice"])
def set_price(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap admin nahi hain!")
    return

  try:
    parts = message.text.split(maxsplit=1)
    price = int(parts[1])

    settings = load_settings()
    settings["price"] = price
    save_settings(settings)

    bot.reply_to(message, f"✅ Price Updated Successfully!\nPrice: ₹{price}RS")
  except Exception as e:
    bot.reply_to(
        message,
        "Galat format! Sahi tareeqa yeh hai:\n`/setprice 100`",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap admin nahi hain!")
    return

  msg_text = message.text.replace("/broadcast", "").strip()
  if not msg_text:
    bot.reply_to(
        message,
        "Kripya message bhi likhein. Jaise:\n`/broadcast Yeh rahe naye"
        " episodes...`",
        parse_mode="Markdown",
    )
    return

  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("SELECT user_id FROM buyers")
  buyers = cursor.fetchall()
  conn.close()

  success_count = 0
  for (user_id,) in buyers:
    try:
      bot.send_message(user_id, msg_text)
      success_count += 1
    except Exception as e:
      pass

  bot.reply_to(
      message,
      f"✅ Broadcast complete! {success_count} users ko message bhej diya gaya"
      " hai.",
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


# User jab photo (screenshot) bhejega
@bot.message_handler(content_types=["photo"])
def handle_screenshot(message):
  # Agar admin ne photo bheji hai toh ignore karein
  if message.from_user.id == ADMIN_ID:
    return

  user_id = message.from_user.id
  username = message.from_user.username or "No Username"
  name = message.from_user.first_name

  # Admin ko screenshot forward karein sath mein Approve/Reject button ke sath
  markup = types.InlineKeyboardMarkup()
  btn_approve = types.InlineKeyboardButton(
      "✅ Approve & Send Access", callback_data=f"approve_{user_id}"
  )
  btn_reject = types.InlineKeyboardButton(
      "❌ Reject", callback_data=f"reject_{user_id}"
  )
  markup.add(btn_approve, btn_reject)

  caption = (
      f"📥 **NEW PAYMENT SCREENSHOT**\n\n"
      f"• Name: {name}\n"
      f"• User ID: `{user_id}`\n"
      f"• Username: @{username}"
  )

  # Admin ke paas photo aur buttons bhej dein
  bot.send_photo(
      ADMIN_ID,
      message.photo[-1].file_id,
      caption=caption,
      reply_markup=markup,
      parse_mode="Markdown",
  )
  bot.reply_to(
      message,
      "✅ Aapka screenshot mil gaya hai! Admin verification ke baad aapko"
      " episodes mil jayenge.",
  )


# Admin jab Approve ya Reject button par click karega
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("approve_")
    or call.data.startswith("reject_")
)
def handle_approval(call):
  if call.from_user.id != ADMIN_ID:
    bot.answer_callback_query(
        call.id, "Aap yeh action nahi le sakte!", show_alert=True
    )
    return

  action, user_id_str = call.data.split("_")
  target_user_id = int(user_id_str)

  if action == "approve":
    # User ko database mein save karein taaki future update mil sake
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO buyers (user_id) VALUES (?)", (target_user_id,)
    )
    conn.commit()
    conn.close()

    # User ko success message aur episodes link/files bhejein
    settings = load_settings()
    start_ep = settings["start_ep"]
    end_ep = settings["end_ep"]

    user_msg = (
        f"🎉 **Payment Approved Successfully!**\n\n"
        f"Aapke episodes ({start_ep} - {end_ep}) ki delivery yeh rahi:\n"
        f"[Yahan apna channel link ya episodes file daalein]"
    )
    try:
      bot.send_message(target_user_id, user_msg, parse_mode="Markdown")
      bot.answer_callback_query(
          call.id, "Payment approved & access sent successfully!"
      )
      bot.edit_message_caption(
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          caption=call.message.caption + "\n\n**[ STATUS: APPROVED ✅ ]**",
          parse_mode="Markdown",
          reply_markup=None,
      )
    except Exception as e:
      bot.answer_callback_query(
          call.id, f"Error sending message to user: {e}", show_alert=True
      )

  elif action == "reject":
    try:
      bot.send_message(
          target_user_id,
          "❌ Aapka payment screenshot reject kar diya gaya hai. Kripya sahi"
          " payment karke dobara bhejein.",
      )
      bot.answer_callback_query(call.id, "Payment rejected.")
      bot.edit_message_caption(
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          caption=call.message.caption + "\n\n**[ STATUS: REJECTED ❌ ]**",
          parse_mode="Markdown",
          reply_markup=None,
      )
    except Exception as e:
      bot.answer_callback_query(
          call.id, f"Error rejecting: {e}", show_alert=True
      )


if __name__ == "__main__":
  RENDER_URL = os.environ.get(
      "RENDER_EXTERNAL_URL", "https://badmash-4k97.onrender.com"
  )
  bot.remove_webhook()
  bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")

  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
  
