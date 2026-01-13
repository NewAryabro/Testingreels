from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import os

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi 👋\nSend me text and I will convert it to voice 🎙️"
    )

async def text_to_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    tts = gTTS(text=text, lang='en')  # Telugu -> 'te'
    file = "voice.mp3"
    tts.save(file)

    await update.message.reply_audio(audio=open(file, 'rb'))
    os.remove(file)

app = ApplicationBuilder().token("6214130906:AAEIJXHDUvYjbUVLIBB9FELILdlDergk0a4").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_voice))

app.run_polling()
