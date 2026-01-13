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

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")

VOICE_MAP = {
    "te_m": "te-IN-MohanNeural",
    "te_f": "te-IN-ShrutiNeural",
    "en_m": "en-US-GuyNeural",
    "en_f": "en-US-JennyNeural"
}
# ----------------------------------------

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()  # only clear on /start
    await update.message.reply_text(
        "🎙️ Reels Voice Bot\n\n"
        "1️⃣ Text send cheyyi\n"
        "2️⃣ Voice select cheyyi\n"
        "3️⃣ Generate press cheyyi"
    )

# ---------------- TEXT ----------------
async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ❌ DO NOT CLEAR context.user_data here
    context.user_data["text"] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("👨 Male", callback_data="gender_m"),
            InlineKeyboardButton("👩 Female", callback_data="gender_f")
        ],
        [
            InlineKeyboardButton("🇮🇳 Telugu", callback_data="lang_te"),
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton("🎙️ Generate", callback_data="generate")
        ]
    ]

    await update.message.reply_text(
        "Options select cheyyi 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- BUTTON HANDLER ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ---------- Gender ----------
    if data == "gender_m":
        context.user_data["gender"] = "m"
        await query.message.reply_text("👨 Male selected")
        return

    if data == "gender_f":
        context.user_data["gender"] = "f"
        await query.message.reply_text("👩 Female selected")
        return

    # ---------- Language ----------
    if data == "lang_te":
        context.user_data["lang"] = "te"
        await query.message.reply_text("🇮🇳 Telugu selected")
        return

    if data == "lang_en":
        context.user_data["lang"] = "en"
        await query.message.reply_text("🇺🇸 English selected")
        return

    # ---------- Generate ----------
    if data == "generate":
        text = context.user_data.get("text")
        gender = context.user_data.get("gender")
        lang = context.user_data.get("lang")

        if not text or not gender or not lang:
            await query.message.reply_text(
                "❌ Please select Text + Gender + Language first"
            )
            return

        voice = VOICE_MAP[f"{lang}_{gender}"]

        # 🔥 SSML for natural pauses & emotion
        ssml_text = f"""
<speak>
    <prosody rate="85%" pitch="+2Hz">
        {text.replace("...", "<break time='700ms'/>")}
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

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # ⚠️ ORDER MATTERS
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))  # callback first
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))

    app.run_polling()

if __name__ == "__main__":
    main()
