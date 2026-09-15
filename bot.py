import os
import telebot
from telebot import types
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# --- CONFIGURATION ---
TOKEN = "YOUR_BOT_TOKEN"  # Apna Bot Token yahan daalein
ADMIN_ID = 6817248389     # Aapki Admin ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- FLASK ROUTES (Render ke liye zaroori) ---
@app.route('/')
def home():
    return "Bot is running live!"

# --- TELEGRAM BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("✨ Buy Access / Pre-Book", callback_data="buy_access")
    markup.add(btn)
    bot.reply_to(message, "Namaste! Super Yoddha series ke liye niche diye gaye button par click karein.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "buy_access")
def handle_buy(call):
    bot.answer_callback_query(call.id)
    # Yahan aap apna QR code ya payment details bhej sakte hain
    bot.send_message(
        call.message.chat.id, 
        "⚡ **SUPER YODDHA PAYMENT QR CODE** ⚡\n\n"
        "• UPI ID: badmashromeo0007@okaxis\n"
        "• Amount: ₹100\n\n"
        "1. Is QR code ko scan karke payment karein.\n"
        "2. Payment karne ke baad screenshot yahin bot mein bhej dein."
    )

# Screenshot handle karne ke liye handler
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user = message.from_user
    caption = (
        f"📥 **NEW PAYMENT / PRE-BOOK SCREENSHOT**\n\n"
        f"• Name: {user.first_name}\n"
        f"• User ID: {user.id}\n"
        f"• Username: @{user.username if user.username else 'N/A'}"
    )
    
    # Admin ke paas approval buttons ke sath bhejien
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ Approve & Send Uniq", callback_data=f"approve_{user.id}")
    reject_btn = types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
    markup.add(approve_btn, reject_btn)
    
    # Admin ko forward karein
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup)
    bot.reply_to(message, "✅ Aapka screenshot mil gaya hai! Admin verification ke baad aapko update mil jayega.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_admin_action(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
        return
        
    action, target_user_id = call.data.split('_')
    target_user_id = int(target_user_id)
    
    if action == 'approve':
        bot.answer_callback_query(call.id, "Approved successfully!")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ✅ APPROVED")
        # User ko unique invite link bhejien
        bot.send_message(target_user_id, "🎉 Aapka payment verify ho gaya hai! Yeh raha aapka unique channel join link: [Yahan Link Dalein]")
    else:
        bot.answer_callback_query(call.id, "Rejected!")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ❌ REJECTED")
        bot.send_message(target_user_id, "❌ Aapka payment screenshot reject kar diya gaya hai. Kripya sahi details ke sath dobara koshish karein.")

# --- APSCHEDULER SETUP ---
scheduler = BackgroundScheduler()
scheduler.start()

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # Render ke dynamic port ko uthane ke liye
    port = int(os.environ.get("PORT", 5000))
    
    # Bot ko background thread mein ya polling par chalane ke liye (Agar Webhook use nahi kar rahe toh bot.infinity_polling use karein)
    import threading
    polling_thread = threading.Thread(target=bot.infinity_polling, daemon=True)
    polling_thread.start()
    
    # Flask app ko start karein taaki Render ka port scan timeout error na aaye
    app.run(host='0.0.0.0', port=port)
  
