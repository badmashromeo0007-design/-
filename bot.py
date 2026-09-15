import json
import os
import sqlite3
from flask import Flask, request
import telebot
from telebot import types

TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389  # Aapki Admin ID
CHANNEL_ID = -1004382767346  # Aapka Main Channel ID (Yahan bot Admin hona chahiye)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

SETTINGS_FILE = "bot_settings.json"
DB_FILE = "bot_database.db"


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
        return json.load(f)
    except:
      return default_data
  return default_data


def save_settings(data):
  with open(SETTINGS_FILE, "w") as f:
    json.dump(data, f)


@app.route("/")
def home():
  return "Bot is running 24/7 with Unique Invite Link Support!"


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
      f"  ✅  Verified Store  ·  Auto-Unique Link\n\n"
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


@bot.message_handler(commands=["post"])
def post_to_channel(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap admin nahi hain!")
    return

  if message.reply_to_message:
    try:
      bot.copy_message(
          chat_id=CHANNEL_ID,
          from_chat_id=message.chat.id,
          message_id=message.reply_to_message.message_id,
      )
      bot.reply_to(message, "✅ Post successfully channel par bhej di gayi hai!")
    except Exception as e:
      bot.reply_to(message, f"❌ Error: {e}")
  else:
    text_to_send = message.text.replace("/post", "").strip()
    if text_to_send:
      try:
        markup = types.InlineKeyboardMarkup()
        btn_dm = types.InlineKeyboardButton(
            "📥 Click Here To Buy / DM", url="https://t.me/Romeo_pay_bot"
        )
        markup.add(btn_dm)

        bot.send_message(
            CHANNEL_ID,
            text_to_send,
            reply_markup=markup,
            parse_mode="Markdown",
        )
        bot.reply_to(
            message,
            "✅ Message aur clickable button successfully channel par bhej diya"
            " gaya hai!",
        )
      except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")
    else:
      bot.reply_to(
          message,
          "⚠️ Sahi tareeqa:\n1. Kisi bhi message/photo ko reply karke"
          " `/post` likhein.\n2. Ya fir `/post [Aapka Message]` likhein.",
      )


@bot.callback_query_handler(func=lambda call: call.data == "get_qr")
def qr_handler(call):
  settings = load_settings()
  start_ep = settings.get("start_ep", 3517)
  end_ep = settings.get("end_ep", 3526)
  price = settings.get("price", 50)
  upi = settings.get("upi_id", "badmashromeo0007@okaxis")

  upi_link = (
      f"upi://pay?pa={upi}&pn=SuperYoddha&am={price}&cu=INR&tn=Episodes"
      f"%20{start_ep}%20to%20{end_ep}"
  )
  qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_link}"

  caption = (
      f"⚡ **SUPER YODDHA PAYMENT QR CODE** ⚡\n\n"
      f"• UPI ID: `{upi}`\n"
      f"• Amount: ₹{price}\n"
      f"• Episodes: {start_ep} TO {end_ep}\n\n"
      f"1. Is QR code ko scan karke payment karein.\n"
      f"2. Payment karne ke baad screenshot yahin bot mein bhej dein."
  )

  try:
    bot.send_photo(
        call.message.chat.id, qr_url, caption=caption, parse_mode="Markdown"
    )
  except Exception as e:
    bot.send_message(
        call.message.chat.id,
        caption + f"\n\n*(Error generating QR: {e})*",
        parse_mode="Markdown",
    )


@bot.callback_query_handler(func=lambda call: call.data == "get_prebook_qr")
def prebook_qr_handler(call):
  settings = load_settings()
  p_start = settings.get("pre_start", 3527)
  p_end = settings.get("pre_end", 3535)
  p_price = settings.get("pre_price", 70)
  upi = settings.get("upi_id", "badmashromeo0007@okaxis")

  upi_link = (
      f"upi://pay?pa={upi}&pn=SuperYoddhaPreBook&am={p_price}&cu=INR&tn=PreBook"
      f"%20{p_start}%20to%20{p_end}"
  )
  qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_link}"

  caption = (
      f"🚀 **PRE-BOOKING QR CODE** 🚀\n\n"
      f"• Upcoming Episodes: {p_start} TO {p_end}\n"
      f"• Pre-Book Price: ₹{p_price}\n"
      f"• UPI ID: `{upi}`\n\n"
      f"1. Is QR code par payment karke advance booking karein.\n"
      f"2. Payment ka screenshot yahin bot mein bhej dein taaki aapka slot"
      f" secure ho sake."
  )

  try:
    bot.send_photo(
        call.message.chat.id, qr_url, caption=caption, parse_mode="Markdown"
    )
  except Exception as e:
    bot.send_message(
        call.message.chat.id,
        caption + f"\n\n*(Error generating QR: {e})*",
        parse_mode="Markdown",
    )


@bot.message_handler(content_types=["photo"])
def handle_screenshot(message):
  user_id = message.from_user.id
  username = message.from_user.username or "No Username"
  name = message.from_user.first_name

  markup = types.InlineKeyboardMarkup()
  btn_approve = types.InlineKeyboardButton(
      "✅ Approve & Send Unique Link", callback_data=f"approve_{user_id}"
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
    try:
      # Har user ke liye ek naya alag (unique) invite link generate karna
      invite_link = bot.create_chat_invite_link(
          chat_id=CHANNEL_ID,
          member_limit=1,  # Yeh link sirf ek hi user ke liye chalega
      )
      unique_link = invite_link.invite_link

      user_msg = (
          f"🎉 **Payment / Pre-Booking Approved!**\n\n"
          f"Aapka payment verify ho gaya hai! Yahan aapka personal invite link"
          f" hai (Yeh sirf aapke liye hai):\n🔗 **{unique_link}**"
      )

      bot.send_message(target_user_id, user_msg, parse_mode="Markdown")
      bot.answer_callback_query(
          call.id, "Approved & Unique Link Sent to User!"
      )
      bot.edit_message_caption(
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          caption=call.message.caption
          + f"\n\n**[ STATUS: APPROVED ✅ ]**\nLink: `{unique_link}`",
          parse_mode="Markdown",
          reply_markup=None,
      )
    except Exception as e:
      bot.answer_callback_query(
          call.id, f"Error generating link: {e}", show_alert=True
      )

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
  
