import json
import os
import sqlite3
from flask import Flask, request
import telebot
from telebot import types

TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389  # Aapki Admin ID
CHANNEL_ID = -1004382767346  # Aapka Main Channel ID

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
  cursor.execute(
      """CREATE TABLE IF NOT EXISTS pre_bookings (
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
      "start_ep": 3517,
      "end_ep": 3526,
      "price": 50,
      "total_eps": 6,
      "upi_id": "badmashromeo0007@okaxis",
      "pre_start": 3527,
      "pre_end": 3535,
      "pre_price": 70,
  }
  if os.path.exists(SETTINGS_FILE):
    try:
      with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)
        # Ensure pre-booking keys exist
        if "pre_start" not in data:
          data["pre_start"] = 3527
          data["pre_end"] = 3535
          data["pre_price"] = 70
        return data
    except:
      return default_data
  return default_data


def save_settings(data):
  with open(SETTINGS_FILE, "w") as f:
    json.dump(data, f)


@app.route("/")
def home():
  return "Bot is running 24/7 with Pre-Booking Support!"


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
  start_ep = settings.get("start_ep", 3517)
  end_ep = settings.get("end_ep", 3526)
  price = settings.get("price", 50)
  total_eps = settings.get("total_eps", (end_ep - start_ep) + 1)

  text = (
      f"🎧  **EPISODE PACK**\n"
      f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
      f"  ◆  🎵  Episode  {start_ep}  →  {end_ep}\n"
      f"  ◆  📦  {total_eps} Episodes  ·  Full Audio Access\n\n"
      f"·  ·  ·  ·  ·  ·  ·  ·  ·  ·\n\n"
      f"  ◆  💰  Price      ›  {price} ₹\n"
      f"  ◆  ⚡  Instant Delivery  ·  Access immediately\n\n"
      f"·  ·  ·  ·  ·  ·  ·  ·  ·  ·\n\n"
      f"  🔐  QR Payment  ·  100% Secure\n"
      f"  ✅  Verified Store  ·  Instant Auto-Delivery\n\n"
      f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  )

  markup = types.InlineKeyboardMarkup()
  btn_pay = types.InlineKeyboardButton(
      "💳 Pay Now (Get QR Code)", callback_data="get_qr"
  )
  btn_prebook = types.InlineKeyboardButton(
      "🚀 Pre-Book Upcoming Episodes", callback_data="get_prebook_qr"
  )
  markup.add(btn_pay)
  markup.add(btn_prebook)

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
    total_eps = (end_ep - start_ep) + 1

    settings = load_settings()
    settings["start_ep"] = start_ep
    settings["end_ep"] = end_ep
    settings["total_eps"] = total_eps
    save_settings(settings)

    bot.reply_to(
        message,
        f"✅ Episodes Updated Successfully!\nRange: {start_ep} →"
        f" {end_ep}\nTotal: {total_eps} Episodes",
    )
  except Exception as e:
    bot.reply_to(
        message,
        "Galat format! Sahi tareeqa yeh hai:\n`/setep 3517 3526`",
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

    bot.reply_to(message, f"✅ Price Updated Successfully!\nPrice: ₹{price}")
  except Exception as e:
    bot.reply_to(
        message,
        "Galat format! Sahi tareeqa yeh hai:\n`/setprice 50`",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["setprebook"])
def set_prebook(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap admin nahi hain!")
    return

  try:
    # Format: /setprebook 3527 3535 70
    parts = message.text.replace("/setprebook", "").strip().split()
    p_start = int(parts[0])
    p_end = int(parts[1])
    p_price = int(parts[2])

    settings = load_settings()
    settings["pre_start"] = p_start
    settings["pre_end"] = p_end
    settings["pre_price"] = p_price
    save_settings(settings)

    bot.reply_to(
        message,
        f"✅ Pre-Booking Details Updated!\nRange: {p_start} →"
        f" {p_end}\nPrice: ₹{p_price}",
    )
  except Exception as e:
    bot.reply_to(
        message,
        "Galat format! Sahi tareeqa yeh hai:\n`/setprebook 3527 3535 70`",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["setpost", "push"])
def push_menu_to_channel(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap admin nahi hain!")
    return

  settings = load_settings()
  start_ep = settings.get("start_ep", 3517)
  end_ep = settings.get("end_ep", 3526)
  price = settings.get("price", 50)
  total_eps = settings.get("total_eps", (end_ep - start_ep) + 1)

  text = (
      f"🎧  **EPISODE PACK**\n"
      f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
      f"  ◆  🎵  Episode  {start_ep}  →  {end_ep}\n"
      f"  ◆  📦  {total_eps} Episodes  ·  Full Audio Access\n\n"
      f"·  ·  ·  ·  ·  ·  ·  ·  ·  ·\n\n"
      f"  ◆  💰  Price      ›  {price} ₹\n"
      f"  ◆  ⚡  Instant Delivery  ·  Access immediately\n\n"
      f"·  ·  ·  ·  ·  ·  ·  ·  ·  ·\n\n"
      f"  🔐  QR Payment  ·  100% Secure\n"
      f"  ✅  Verified Store  ·  Instant Auto-Delivery\n\n"
      f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  )

  markup = types.InlineKeyboardMarkup()
  btn_bot = types.InlineKeyboardButton(
      "💳 Get Episodes Now", url="https://t.me/ROMEO_bot"
  )
  markup.add(btn_bot)

  try:
    bot.send_message(
        CHANNEL_ID, text, reply_markup=markup, parse_mode="Markdown"
    )
    bot.reply_to(message, "✅ Menu successfully main channel par post ho gaya hai!")
  except Exception as e:
    bot.reply_to(message, f"❌ Error: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "get_qr")
def qr_handler(call):
  settings = load_settings()
  start_ep = settings.get("start_ep", 3517)
  end_ep = settings.get("end_ep", 3526)
  price = settings.get("price", 50)
  upi = settings.get("upi_id", "badmashromeo0007@okaxis")

  caption = (
      f"⚡ **PAYMENT QR CODE** ⚡\n\n"
      f"• UPI ID: `{upi}`\n"
      f"• Amount: ₹{price}\n"
      f"• Episodes: {start_ep} TO {end_ep}\n\n"
      f"1. Is QR code ko scan karke payment karein.\n"
      f"2. Payment karne ke baad screenshot yahin bot mein bhej dein."
  )

  qr_found = False
  for filename in ["qr.jpg", "qr.png", "QR.jpg", "QR.png"]:
    if os.path.exists(filename):
      try:
        with open(filename, "rb") as photo:
          bot.send_photo(
              call.message.chat.id,
              photo,
              caption=caption,
              parse_mode="Markdown",
          )
        qr_found = True
        break
      except:
        pass

  if not qr_found:
    bot.send_message(
        call.message.chat.id,
        caption + "\n\n*(Note: QR image server par nahi mili)*",
        parse_mode="Markdown",
    )


@bot.callback_query_handler(func=lambda call: call.data == "get_prebook_qr")
def prebook_qr_handler(call):
  settings = load_settings()
  p_start = settings.get("pre_start", 3527)
  p_end = settings.get("pre_end", 3535)
  p_price = settings.get("pre_price", 70)
  upi = settings.get("upi_id", "badmashromeo0007@okaxis")

  caption = (
      f"🚀 **PRE-BOOKING QR CODE** 🚀\n\n"
      f"• Upcoming Episodes: {p_start} TO {p_end}\n"
      f"• Pre-Book Price: ₹{p_price}\n"
      f"• UPI ID: `{upi}`\n\n"
      f"1. Is QR code par payment karke advance booking karein.\n"
      f"2. Payment ka screenshot yahin bot mein bhej dein taaki aapka slot"
      f" secure ho sake."
  )

  qr_found = False
  for filename in ["qr.jpg", "qr.png", "QR.jpg", "QR.png"]:
    if os.path.exists(filename):
      try:
        with open(filename, "rb") as photo:
          bot.send_photo(
              call.message.chat.id,
              photo,
              caption=caption,
              parse_mode="Markdown",
          )
        qr_found = True
        break
      except:
        pass

  if not qr_found:
    bot.send_message(
        call.message.chat.id,
        caption + "\n\n*(Note: QR image server par nahi mili)*",
        parse_mode="Markdown",
    )


@bot.message_handler(content_types=["photo"])
def handle_screenshot(message):
  if message.from_user.id == ADMIN_ID:
    return

  user_id = message.from_user.id
  username = message.from_user.username or "No Username"
  name = message.from_user.first_name

  markup = types.InlineKeyboardMarkup()
  btn_approve = types.InlineKeyboardButton(
      "✅ Approve & Send Access", callback_data=f"approve_{user_id}"
  )
  btn_reject = types.InlineKeyboardButton(
      "❌ Reject", callback_data=f"reject_{user_id}"
  )
  markup.add(btn_approve, btn_reject)

  caption = (
      f"📥 **NEW PAYMENT / PRE-BOOK SCREENSHOT**\n\n"
      f"• Name: {name}\n"
      f"• User ID: `{user_id}`\n"
      f"• Username: @{username}"
  )

  bot.send_photo(
      ADMIN_ID,
      message.photo[-1].file_id,
      caption=caption,
      reply_markup=markup,
      parse_mode="Markdown",
  )
  bot.reply_to(
      message,
      "✅ Aapka screenshot mil gaya hai! Admin verification ke baad aapko update"
      " mil jayega.",
  )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("approve_")
    or call.data.startswith("reject_")
)
def handle_approval(call):
  if call.from_user.id != ADMIN_ID:
    bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
    return

  action, user_id_str = call.data.split("_")
  target_user_id = int(user_id_str)

  if action == "approve":
    user_msg = (
        f"🎉 **Payment / Pre-Booking Approved!**\n\n"
        f"Aapka slot successfully secure ho gaya hai. Jaise hi episodes aayenge,"
        f" aapko access mil jayega."
    )
    try:
      bot.send_message(target_user_id, user_msg, parse_mode="Markdown")
      bot.answer_callback_query(call.id, "Approved & notified user!")
      bot.edit_message_caption(
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          caption=call.message.caption + "\n\n**[ STATUS: APPROVED ✅ ]**",
          parse_mode="Markdown",
          reply_markup=None,
      )
    except Exception as e:
      bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

  elif action == "reject":
    try:
      bot.send_message(
          target_user_id,
          "❌ Aapka payment screenshot reject kar diya gaya hai.",
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
      bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)


if __name__ == "__main__":
  RENDER_URL = os.environ.get(
      "RENDER_EXTERNAL_URL", "https://badmash-4k97.onrender.com"
  )
  bot.remove_webhook()
  bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")

  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
  
