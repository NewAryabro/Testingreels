import os
import edge_tts
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

# Best free voices
VOICE_MAP = {
    "te_m": "te-IN-MohanNeural",
    "te_f": "te-IN-ShrutiNeural",
    "en_m": "en-US-GuyNeural",
    "en_f": "en-US-JennyNeural"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙️ Text send cheyyi\n"
        "I will generate natural voice with pauses"
    )

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["text"] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("👨 Male", callback_data="m"),
            InlineKeyboardButton("👩 Female", callback_data="f")
        ],
        [
            InlineKeyboardButton("🇮🇳 Telugu", callback_data="te"),
            InlineKeyboardButton("🇺🇸 English", callback_data="en")
        ]
    ]

    await update.message.reply_text(
        "Voice & Language choose cheyyi 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data[query.data] = True

    if (("m" in context.user_data or "f" in context.user_data) and
        ("te" in context.user_data or "en" in context.user_data)):

        gender = "m" if "m" in context.user_data else "f"
        lang = "te" if "te" in context.user_data else "en"
        voice = VOICE_MAP[f"{lang}_{gender}"]

        raw_text = context.user_data["text"]

        # 🔥 SSML for emotion + pauses + speed
        ssml_text = f"""
<speak>
    <prosody rate="85%" pitch="+2Hz">
        {raw_text.replace("...", "<break time='700ms'/>")}
    </prosody>
</speak>
"""

        file = "voice.mp3"
        communicate = edge_tts.Communicate(
            ssml_text,
            voice,
            is_ssml=True
        )
        await communicate.save(file)

        await query.message.reply_audio(
            audio=open(file, "rb"),
            caption="🎧 Ready for reels"
        )

        os.remove(file)
        context.user_data.clear()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
