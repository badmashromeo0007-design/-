import os
import json
from flask import Flask, request
import telebot
import google.generativeai as genai

# Configuration
TOKEN = os.environ.get('BOT_TOKEN', '8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AQ.A80RH6kVs-703IHNMAZ9Bc52mPsf7SluJFwZQ91cduTud2jKjw')

# Initialize Bot and Flask
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Configure Gemini AI Directly with your key
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Gemini Init Error: {e}")
        gemini_model = None
else:
    gemini_model = None

# Render Read-Only File System Bypass using /tmp
DATA_FILE = "/tmp/user_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Save error: {e}")

# Flask webhook Route to fix 404 Not Found Error
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

# Health Check Route
@app.route('/')
def index():
    return "The Super Yoddha Bot is running live!"

# Telegram Command Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Namaste {user_name}! 🙏\n\n"
        "Welcome to **The Super Yoddha Bot**.\n\n"
        "🎬 **Latest Available Content:**\n"
        "• Episodes: **EP 3517 - 3526**\n"
        "• Price: **₹70**\n"
        "• Delivery: **Turant Milega ⚡**\n\n"
        "📢 **Hamare main channel par episodes dale jate hain, kripya channel join karein:**\n"
        "👉 [The Super Yoddha Channel](https://t.me/+gy8gewj0snllZThl)"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    if gemini_model:
        try:
            response = gemini_model.generate_content(
                f"You are the assistant for The Super Yoddha Bot. Current available stock is Episodes 3517 to 3526 for ₹70, available instantly (turant milega). User query: {user_text}"
            )
            if response and response.text:
                bot.reply_to(message, response.text)
            else:
                bot.reply_to(message, "Kshama karein, AI se koi response nahi mila.")
        except Exception as e:
            print(f"Gemini Generation Error: {e}")
            bot.reply_to(message, "Kshama karein, AI response generate karne mein samasya aayi.")
    else:
        bot.reply_to(message, f"Aapka sandesh mila: {user_text}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
