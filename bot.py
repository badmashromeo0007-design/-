# 1. Zaroori AI aur Telegram Libraries Install Karein
!pip install -q TTS python-telegram-bot torch

import os
import torch
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from TTS.api import TTS

# 2. Configuration Parameters
TELEGRAM_BOT_TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"
REFERENCE_AUDIO_PATH = "my_studio_voice.wav"  # Uploaded file name

# 3. Model Loading (Colab Free GPU par Fast Speed)
print("⏳ Coqui XTTS v2 Model load ho raha hai (GPU active)...")
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("✅ Voice Model Successfully Load Ho Gaya!")


# 4. Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "🎙 *Super Yoddha Voice Cloning Bot (Google Colab Live)!*\n\n"
      "Aap jo bhi script text bhejenge, bot use aapki **13-minute studio"
      " audio** wali voice me convert karke reply dega!"
  )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_text = update.message.text
  chat_id = update.message.chat_id

  if not os.path.exists(REFERENCE_AUDIO_PATH):
    await update.message.reply_text(
        f"❌ File Error: '{REFERENCE_AUDIO_PATH}' Colab Files panel me nahi"
        " mili! Kripya file upload karein."
    )
    return

  msg = await update.message.reply_text(
      "⏳ Studio Cloned Voice me audio generate ho raha hai..."
  )

  output_path = f"output_{chat_id}.wav"

  try:
    # XTTS v2 Audio Generation
    tts.tts_to_file(
        text=user_text,
        speaker_wav=REFERENCE_AUDIO_PATH,  # Super Yoddha studio voice
        language="hi",  # Hindi Language Accent
        file_path=output_path,
    )

    await msg.delete()

    # Audio message Telegram par bhejna
    with open(output_path, "rb") as audio:
      await update.message.reply_audio(
          audio=audio, title="Super Yoddha Cloned Audio"
      )

    # Clean up temporary output file
    if os.path.exists(output_path):
      os.remove(output_path)

  except Exception as e:
    await msg.edit_text(f"❌ Error Aaya: {str(e)}")


# 5. Bot Main Loop Run Karein
def main():
  app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(
      MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text)
  )

  print("\n🤖 Telegram Bot LIVE aur Ready Hai! Telegram par text bhejein...")
  app.run_polling()


if __name__ == "__main__":
  main()
