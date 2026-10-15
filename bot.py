import os
from flask import Flask, request
import telebot

TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

ADMIN_ID = 6817248389
CHANNEL_ID = -1004382767346
UPI_ID = "Badmashromeo0007@okaxis"
RENDER_URL = (
    "https://badmash-4k97.onrender.com"  # Apne Render URL se replace karein
)

# User ki selected episode store karne ke liye temporary dictionary
pending_orders = {}


@app.route("/")
def home():
  return "Bot is running successfully with all features!"


@app.route("/set_webhook")
def set_webhook():
  try:
    webhook_url = f"{RENDER_URL}/webhook"
    bot.remove_webhook()
    s = bot.set_webhook(url=webhook_url)
    if s:
      return f"✅ Webhook successfully set to: {webhook_url}"
    else:
      return "❌ Webhook setup failed!", 400
  except Exception as e:
    return f"Error: {str(e)}", 500


# /start command handler (Episodes & Prices list)
@bot.message_handler(commands=["start"])
def send_welcome(message):
  markup = telebot.types.InlineKeyboardMarkup()
  btn1 = telebot.types.InlineKeyboardButton(
      "🎬 Episode 3724-3728 - ₹20", callback_data="buy_ep_3724_3728"
  )
  btn2 = telebot.types.InlineKeyboardButton(
      "🎬 Episode 3729-3733 - ₹20", callback_data="buy_ep_3729_3733"
  )
  markup.add(btn1)
  markup.add(btn2)

  text = (
      "🚀 *Super Yoddha Paid Channel Bot*\n\n"
      "Neeche diye gaye episodes mein se select karein jise aap purchase karna chahte hain:"
  )
  bot.send_message(
      message.chat.id, text, parse_mode="Markdown", reply_markup=markup
  )


# Callback query for episode selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_ep_"))
def handle_buy(call):
  ep_name = call.data.replace("buy_ep_", "").replace("_", "-")
  price = "20"

  pending_orders[call.from_user.id] = ep_name

  text = (
      f"📦 *Selected Episode:* {ep_name}\n"
      f"💰 *Price:* ₹{price}\n\n"
      f"1️⃣ Is UPI ID par payment karein: `{UPI_ID}`\n"
      "2️⃣ Payment karne ke baad **Payment ka Screenshot** ishi bot par bhej dein.\n"
      "3️⃣ Screenshot bhejte hi admin ke paas approval ke liye chala jayega."
  )
  bot.answer_callback_query(call.id)
  bot.send_message(call.message.chat.id, text, parse_mode="Markdown")


# Handle Photos (Payment Screenshots) sent by users
@bot.message_handler(content_types=["photo"])
def handle_screenshot(message):
  user_id = message.from_user.id
  username = (
      message.from_user.username
      if message.from_user.username
      else "No Username"
  )
  ep_name = pending_orders.get(user_id, "Custom Episode")

  # Admin ke paas Approve / Reject buttons ke sath screenshot bhejna
  markup = telebot.types.InlineKeyboardMarkup()
  approve_btn = telebot.types.InlineKeyboardButton(
      "✅ Approve", callback_data=f"app_{user_id}_{ep_name}"
  )
  reject_btn = telebot.types.InlineKeyboardButton(
      "❌ Reject", callback_data=f"rej_{user_id}"
  )
  markup.add(approve_btn, reject_btn)

  caption = (
      f"💰 *Naya Payment Screenshot Aaya Hai!*\n\n"
      f"👤 User: @{username} (ID: `{user_id}`)\n"
      f"🎬 Episode: {ep_name}"
  )

  bot.send_photo(
      ADMIN_ID,
      message.photo[-1].file_id,
      caption=caption,
      parse_mode="Markdown",
      reply_markup=markup,
  )
  bot.reply_to(
      message,
      "✅ Aapka screenshot admin ke paas bhej diya gaya hai. Approval ke baad"
      " aapko link mil jayega!",
  )


# Admin Approval / Rejection Handler
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("app_")
    or call.data.startswith("rej_")
)
def handle_admin_action(call):
  if call.from_user.id != ADMIN_ID:
    bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
    return

  data_parts = call.data.split("_")
  action = data_parts[0]
  target_user_id = int(data_parts[1])

  if action == "app":
    ep_name = data_parts[2]
    try:
      # Channel ka private invite link generate karna (1 use ke liye)
      invite_link = bot.create_chat_invite_link(
          CHANNEL_ID, member_limit=1
      ).invite_link

      # User ko link bhejna
      bot.send_message(
          target_user_id,
          f"🎉 *Payment Approved!*\n\nAapka payment approve ho gaya hai. Yahan aapka private channel link hai:\n{invite_link}",
          parse_mode="Markdown",
      )
      bot.answer_callback_query(call.id, "Approved & Link Sent!")
      bot.edit_message_caption(
          f"✅ *APPROVED* by Admin\nEpisode: {ep_name} for User `{target_user_id}`",
          call.message.chat.id,
          call.message.message_id,
          parse_mode="Markdown",
      )
    except Exception as e:
      bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)

  elif action == "rej":
    bot.send_message(
        target_user_id,
        "❌ *Payment Rejected.*\n\nAapka payment screenshot reject kar diya gaya"
        " hai. Kripya saaf screenshot ya sahi payment details bhejein.",
        parse_mode="Markdown",
    )
    bot.answer_callback_query(call.id, "Rejected!")
    bot.edit_message_caption(
        f"❌ *REJECTED* by Admin for User `{target_user_id}`",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
    )


# 📢 Admin Command to Post directly to Main Channel: /post <message>
@bot.message_handler(commands=["post"])
def admin_post_to_channel(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "Aap yeh command use nahi kar sakte.")
    return

  text_to_post = message.text.replace("/post", "").strip()
  if not text_to_post:
    bot.reply_to(
        message,
        "Kripya /post ke baad message likhein. Jaise:\n`/post New Episode"
        " Uploaded!`",
        parse_mode="Markdown",
    )
    return

  try:
    bot.send_message(CHANNEL_ID, text_to_post, parse_mode="Markdown")
    bot.reply_to(message, "✅ Post successfully main channel par bhej di gayi hai!")
  except Exception as e:
    bot.reply_to(message, f"❌ Error: {str(e)}")


@app.route("/webhook", methods=["POST"])
def webhook():
  json_string = request.get_data().decode("utf-8")
  update = telebot.types.Update.de_json(json_string)
  bot.process_new_updates([update])
  return "", 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
