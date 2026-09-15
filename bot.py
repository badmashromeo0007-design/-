import os
import telebot
from telebot import types
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# --- CONFIGURATION ---
TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389  # Aapki Admin ID

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

app = Flask(__name__)

# --- DYNAMIC SETTINGS (Admin inhe chat se badal sakta hai) ---
bot_settings = {
    "price": "100",
    "episodes": "3527 TO 3537",
    "link": "https://t.me/+-Zv45jwRBJUyYjE1"
}

@app.route('/')
def home():
    return "Bot is running live 24/7!"

# --- ADMIN COMMANDS TO UPDATE SETTINGS ---
@bot.message_handler(commands=['setprice'])
def set_price(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["price"] = parts[1]
        bot.reply_to(message, f"✅ Price Updated Successfully!\nNew Price: ₹{bot_settings['price']}")
    else:
        bot.reply_to(message, "⚠️ Kripya price likhein. Example: /setprice 100")

@bot.message_handler(commands=['setep'])
def set_episodes(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["episodes"] = parts[1]
        bot.reply_to(message, f"✅ Episodes Updated Successfully!\nNew Range: {bot_settings['episodes']}")
    else:
        bot.reply_to(message, "⚠️ Kripya range likhein. Example: /setep 3527 - 3537")

@bot.message_handler(commands=['setlink'])
def set_link(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["link"] = parts[1]
        bot.reply_to(message, f"✅ Invite Link Updated Successfully!\nNew Link: {bot_settings['link']}")
    else:
        bot.reply_to(message, "⚠️ Kripya link likhein. Example: /setlink https://t.me/...")

# --- USER COMMANDS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("✨ Pay Now (Get QR Code)", callback_data="buy_access")
    markup.add(btn)
    
    welcome_text = (
        f"🎧 **EPISODE PACK**\n\n"
        f"• 📻 Episodes: {bot_settings['episodes']}\n"
        f"• 💰 Price: ₹{bot_settings['price']}\n\n"
        "Niche diye gaye button par click karke payment details prapt karein."
    )
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "buy_access")
def handle_buy(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id, 
        f"⚡ **SUPER YODDHA PAYMENT QR CODE** ⚡\n\n"
        f"• UPI ID: badmashromeo0007@okaxis\n"
        f"• Amount: ₹{bot_settings['price']}\n"
        f"• Episodes: {bot_settings['episodes']}\n\n"
        "1. Is QR code ko scan karke payment karein.\n"
        "2. Payment karne ke baad screenshot yahin bot mein bhej dein."
    )

# --- SCREENSHOT HANDLER ---
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user = message.from_user
    bot.reply_to(message, "✅ Aapka screenshot mil gaya hai! Verification ke liye admin ke paas bhej diya gaya hai.")
    
    caption = (
        "📥 NEW PAYMENT SCREENSHOT\n\n"
        f"• Name: {user.first_name}\n"
        f"• User ID: {user.id}\n"
        f"• Username: @{user.username if user.username else 'N/A'}"
    )
    
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}")
    reject_btn = types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
    markup.add(approve_btn, reject_btn)
    
    try:
        photo_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, photo_id, caption=caption, reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Error forwarding photo to admin: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_admin_action(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
        return
        
    action, target_user_id = call.data.split('_')
    target_user_id = int(target_user_id)
    
    if action == 'approve':
        bot.answer_callback_query(call.id, "Approved successfully!")
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ✅ APPROVED")
        except:
            pass
        # Dynamically jo link set kiya hoga wahi user ko jayega
        bot.send_message(target_user_id, f"🎉 Aapka payment verify ho gaya hai! Yeh raha aapka unique channel join link:\n{bot_settings['link']}")
    else:
        bot.answer_callback_query(call.id, "Rejected!")
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ❌ REJECTED")
        except:
            pass
        bot.send_message(target_user_id, "❌ Aapka payment screenshot reject kar diya gaya hai.")

# --- APSCHEDULER SETUP ---
scheduler = BackgroundScheduler()
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    import threading
    polling_thread = threading.Thread(target=bot.infinity_polling, daemon=True)
    polling_thread.start()
    
    app.run(host='0.0.0.0', port=port)
    
