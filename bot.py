import os
import telebot
from telebot import types
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# --- CONFIGURATION ---
TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
ADMIN_ID = 6817248389  # Aapki Admin ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- FLASK ROUTES ---
@app.route('/')
def home():
    return "Bot is running live 24/7!"

# --- TELEGRAM BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("✨ Pay Now (Get QR Code)", callback_data="buy_access")
    markup.add(btn)
    bot.reply_to(message, "Namaste! Super Yoddha series ke liye niche diye gaye button par click karein.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "buy_access")
def handle_buy(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id, 
        "⚡ **SUPER YODDHA PAYMENT QR CODE** ⚡\n\n"
        "• UPI ID: badmashromeo0007@okaxis\n"
        "• Amount: ₹100\n\n"
        "1. Is QR code ko scan karke payment karein.\n"
        "2. Payment karne ke baad screenshot yahin bot mein bhej dein."
    )

# --- FIXED SCREENSHOT HANDLER ---
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user = message.from_user
    
    # User ko turant confirmation bhejiye
    bot.reply_to(message, "✅ Aapka screenshot mil gaya hai! Verification ke liye admin ke paas bhej diya gaya hai.")
    
    caption = (
        f"📥 **NEW PAYMENT SCREENSHOT**\n\n"
        f"• Name: {user.first_name}\n"
        f"• User ID: `{user.id}`\n"
        f"• Username: @{user.username if user.username else 'N/A'}"
    )
    
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}")
    reject_btn = types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
    markup.add(approve_btn, reject_btn)
    
    try:
        photo_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, photo_id, caption=caption, reply_markup=markup, parse_mode="Markdown")
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
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ✅ APPROVED", parse_mode="Markdown")
        bot.send_message(target_user_id, "🎉 Aapka payment verify ho gaya hai! Yeh raha aapka unique channel join link: [Yahan Link Dalein]")
    else:
        bot.answer_callback_query(call.id, "Rejected!")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ❌ REJECTED", parse_mode="Markdown")
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
    
