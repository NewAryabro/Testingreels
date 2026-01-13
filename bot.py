import os
import edge_tts
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")

VOICE_MAP = {
    "te_m": "te-IN-MohanNeural",
    "te_f": "te-IN-ShrutiNeural",
    "en_m": "en-US-GuyNeural",
    "en_f": "en-US-JennyNeural"
}
# =========================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🎙️ Text send cheyyi\n"
        "Reels narration kosam voice generate chestha"
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

    data = query.data

    # Store selections
    if data in ["m", "f"]:
        context.user_data["gender"] = data
    elif data in ["te", "en"]:
        context.user_data["lang"] = data

    # Generate voice only after both selected
    if "gender" in context.user_data and "lang" in context.user_data:
        gender = context.user_data["gender"]
        lang = context.user_data["lang"]

        voice = VOICE_MAP[f"{lang}_{gender}"]
        text = context.user_data.get("text")

        if not text:
            await query.message.reply_text("❌ Text missing. Please send text again.")
            context.user_data.clear()
            return

        # 🔥 SSML for natural pauses & emotion
        ssml_text = f"""
<speak>
    <prosody rate="85%" pitch="+2Hz">
        {text.replace("...", "<break time='700ms'/>")}
    </prosody>
</speak>
"""

        output = "voice.mp3"
        communicate = edge_tts.Communicate(
            ssml_text,
            voice,
            is_ssml=True
        )
        await communicate.save(output)

        await query.message.reply_audio(
            audio=open(output, "rb"),
            caption="🎧 Ready for reels"
        )

        os.remove(output)
        context.user_data.clear()


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # ⚠️ ORDER IS IMPORTANT
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))   # callbacks FIRST
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))

    app.run_polling()


if __name__ == "__main__":
    main()
