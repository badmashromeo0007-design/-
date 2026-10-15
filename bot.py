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

# Aapka Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8831853256:AAGnh4_otfUHxAxU2QgXUIPtZVZut5FPVJU"

# Aapki 13-minute wali studio audio file ka naam (Isko isi folder me rakhna hai)
REFERENCE_AUDIO_PATH = "my_studio_voice.wav"

print("AI Voice Model load ho raha hai, kripya intezaar karein...")
device = "cuda" if torch.cuda.is_available() else "cpu"
# Coqui XTTS v2 multilingual model load ho raha hai
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("Model successfully load ho gaya hai!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "🎙 *Super Yoddha Voice Cloning Bot me Aapka Swagat Hai!*\n\n"
      "Aap jo bhi text message bhejenge, bot use aapki **13-minute wali"
      " studio audio** (Super Yoddha narrator aawaz) me convert karke audio"
      " message bhej dega!"
  )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_text = update.message.text
  chat_id = update.message.chat_id

  if not os.path.exists(REFERENCE_AUDIO_PATH):
    await update.message.reply_text(
        f"❌ Error: '{REFERENCE_AUDIO_PATH}' file nahi mili! Kripya apni 13"
        " minute ki studio audio file ka naam 'my_studio_voice.wav' karke isi"
        " folder me rakhein."
    )
    return

  msg = await update.message.reply_text(
      "⏳ Cloned voice me audio generate ho raha hai, thoda waqt lag sakta"
      " hai..."
  )

  output_path = f"output_{chat_id}.wav"

  try:
    # XTTS v2 ka use karke text ko cloned aawaz me convert karna
    tts.tts_to_file(
        text=user_text,
        speaker_wav=REFERENCE_AUDIO_PATH,  # Aapki 13-min studio file
        language="hi",  # Hindi ke liye 'hi'
        file_path=output_path,
    )

    # Telegram par audio file bhejna
    await msg.delete()
    with open(output_path, "rb") as audio:
      await update.message.reply_audio(
          audio=audio, title="Super Yoddha Cloned Voice"
      )

    # Temporary output file delete karna
    if os.path.exists(output_path):
      os.remove(output_path)

  except Exception as e:
    await msg.edit_text(f"Audio generate karne me error aaya: {str(e)}")


def main():
  app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(
      MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text)
  )

  print("Telegram Bot live aur active hai...")
  app.run_polling()


if __name__ == "__main__":
  main()
