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

# --- DYNAMIC SETTINGS FOR MULTIPLE PACKS ---
bot_settings = {
    "price1": "100",
    "episodes1": "3527 TO 3537",
    "link1": "https://t.me/+-Zv45jwRBJUyYjE1",
    
    "price2": "150",
    "episodes2": "3538 TO 3550",
    "link2": "https://t.me/+AnotherUniqueLinkHere"
}

@app.route('/')
def home():
    return "Bot is running live 24/7!"

# --- ADMIN COMMANDS FOR PACK 1 ---
@bot.message_handler(commands=['setprice1'])
def set_price1(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["price1"] = parts[1]
        bot.reply_to(message, f"✅ Pack 1 Price Updated: ₹{bot_settings['price1']}")
    else:
        bot.reply_to(message, "⚠️ Format: /setprice1 100")

@bot.message_handler(commands=['setep1'])
def set_ep1(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["episodes1"] = parts[1]
        bot.reply_to(message, f"✅ Pack 1 Episodes Updated: {bot_settings['episodes1']}")
    else:
        bot.reply_to(message, "⚠️ Format: /setep1 3527 - 3537")

@bot.message_handler(commands=['setlink1'])
def set_link1(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["link1"] = parts[1]
        bot.reply_to(message, f"✅ Pack 1 Link Updated: {bot_settings['link1']}")
    else:
        bot.reply_to(message, "⚠️ Format: /setlink1 https://t.me/...")


# --- ADMIN COMMANDS FOR PACK 2 ---
@bot.message_handler(commands=['setprice2'])
def set_price2(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["price2"] = parts[1]
        bot.reply_to(message, f"✅ Pack 2 Price Updated: ₹{bot_settings['price2']}")
    else:
        bot.reply_to(message, "⚠️ Format: /setprice2 150")

@bot.message_handler(commands=['setep2'])
def set_ep2(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["episodes2"] = parts[1]
        bot.reply_to(message, f"✅ Pack 2 Episodes Updated: {bot_settings['episodes2']}")
    else:
        bot.reply_to(message, "⚠️ Format: /setep2 3538 - 3550")

@bot.message_handler(commands=['setlink2'])
def set_link2(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_settings["link2"] = parts[1]
        bot.reply_to(message, f"✅ Pack 2 Link Updated: {bot_settings['link2']}")
    else:
        bot.reply_to(message, "⚠️ Format: /setlink2 https://t.me/...")


# --- POST COMMANDS FOR CHANNEL ---
@bot.message_handler(commands=['post1'])
def post_pack1(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("✨ Pay Now (Pack 1)", callback_data="buy_pack1")
    markup.add(btn)
    
    text = (
        f"🎧 **EPISODE PACK 1**\n\n"
        f"• 📻 Episodes: {bot_settings['episodes1']}\n"
        f"• 💰 Price: ₹{bot_settings['price1']}\n\n"
        "Niche diye gaye button par click karke payment karein."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['post2'])
def post_pack2(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("✨ Pay Now (Pack 2)", callback_data="buy_pack2")
    markup.add(btn)
    
    text = (
        f"🎧 **EPISODE PACK 2**\n\n"
        f"• 📻 Episodes: {bot_settings['episodes2']}\n"
        f"• 💰 Price: ₹{bot_settings['price2']}\n\n"
        "Niche diye gaye button par click karke payment karein."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")


# --- CALLBACKS FOR BUY BUTTONS ---
@bot.callback_query_handler(func=lambda call: call.data in ["buy_pack1", "buy_pack2"])
def handle_buy(call):
    bot.answer_callback_query(call.id)
    if call.data == "buy_pack1":
        bot.send_message(
            call.message.chat.id, 
            f"⚡ **PACK 1 PAYMENT QR CODE** ⚡\n\n"
            f"• UPI ID: badmashromeo0007@okaxis\n"
            f"• Amount: ₹{bot_settings['price1']}\n"
            f"• Episodes: {bot_settings['episodes1']}\n\n"
            "1. Is QR code ko scan karke payment karein.\n"
            "2. Screenshot yahin bot mein bhej dein."
        )
    else:
        bot.send_message(
            call.message.chat.id, 
            f"⚡ **PACK 2 PAYMENT QR CODE** ⚡\n\n"
            f"• UPI ID: badmashromeo0007@okaxis\n"
            f"• Amount: ₹{bot_settings['price2']}\n"
            f"• Episodes: {bot_settings['episodes2']}\n\n"
            "1. Is QR code ko scan karke payment karein.\n"
            "2. Screenshot yahin bot mein bhej dein."
        )

# --- STANDARD START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Namaste! Kripya channel par diye gaye posts mein se kisi ek ke 'Pay Now' button par click karein.")

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
    approve_btn = types.InlineKeyboardButton("✅ Approve Pack 1", callback_data=f"approve1_{user.id}")
    approve_btn2 = types.InlineKeyboardButton("✅ Approve Pack 2", callback_data=f"approve2_{user.id}")
    reject_btn = types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
    markup.add(approve_btn, approve_btn2)
    markup.add(reject_btn)
    
    try:
        photo_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, photo_id, caption=caption, reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Error forwarding photo: {e}")

# --- ADMIN APPROVAL HANDLER FOR BOTH PACKS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve1_') or call.data.startswith('approve2_') or call.data.startswith('reject_'))
def handle_admin_action(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Aap admin nahi hain!", show_alert=True)
        return
        
    data_parts = call.data.split('_')
    action = data_parts[0]
    target_user_id = int(data_parts[1])
    
    if action == 'approve1':
        bot.answer_callback_query(call.id, "Pack 1 Approved!")
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ✅ APPROVED (PACK 1)")
        except:
            pass
        bot.send_message(target_user_id, f"🎉 Aapka Pack 1 verify ho gaya hai! Yeh raha aapka link:\n{bot_settings['link1']}")
        
    elif action == 'approve2':
        bot.answer_callback_query(call.id, "Pack 2 Approved!")
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=call.message.caption + "\n\nSTATUS: ✅ APPROVED (PACK 2)")
        except:
            pass
        bot.send_message(target_user_id, f"🎉 Aapka Pack 2 verify ho gaya hai! Yeh raha aapka link:\n{bot_settings['link2']}")
        
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
    
