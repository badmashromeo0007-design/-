import os
import json
from flask import Flask, request
import telebot
import google.generativeai as genai

# Configuration
TOKEN = os.environ.get('BOT_TOKEN')  # Render par BOT_TOKEN environment variable set hona chahiye
GEMINI_API_KEY = "AQ.Ab8RN6K8v-703IMMAZ9BcSS2mPsf1SLujFWZQ91cbd1U2DjXIw"

# Initialize Bot and Flask
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Configure Gemini AI directly with your key
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
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

# Flask Webhook Route to fix 404 Not Found Error
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
        f"Namaste {user_name}! 🙏\n"
        "Welcome to **The Super Yoddha** Bot.\n\n"
        "Aap yahan se audio series links, updates aur premium content manage kar sakte hain."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    if gemini_model:
        try:
            response = gemini_model.generate_content(user_text)
            bot.reply_to(message, response.text)
        except Exception as e:
            bot.reply_to(message, "Kshama karein, AI response generate karne mein samasya aayi.")
    else:
        bot.reply_to(message, f"Aapka sandesh mila: {user_text}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
