import os
import asyncio
import tempfile
import edge_tts
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🎙️ Reels Voice Bot\n\n"
        "Send me the text you want to convert to speech 👇\n\n"
        "Then choose voice → Generate"
    )

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text.strip()

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
        "Text received!\nNow select voice options:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Store selections (they toggle / overwrite)
    if data == "gender_m":
        context.user_data["gender"] = "m"
    elif data == "gender_f":
        context.user_data["gender"] = "f"
    elif data == "lang_te":
        context.user_data["lang"] = "te"
    elif data == "lang_en":
        context.user_data["lang"] = "en"

    # Show current selection status
    if data in ("gender_m", "gender_f", "lang_te", "lang_en"):
        gender = context.user_data.get("gender", "?")
        lang = context.user_data.get("lang", "?")
        await query.edit_message_text(
            f"Current selection:\n"
            f"Gender: {'Male' if gender == 'm' else 'Female' if gender == 'f' else '—'}\n"
            f"Language: {'Telugu' if lang == 'te' else 'English' if lang == 'en' else '—'}\n\n"
            "Choose again or press Generate ↓",
            reply_markup=query.message.reply_markup
        )
        return

    # ── Generate ──
    if data == "generate":
        text = context.user_data.get("text")
        gender = context.user_data.get("gender")
        lang = context.user_data.get("lang")

        if not text:
            await query.message.reply_text("❌ No text provided")
            return
        if not gender or not lang:
            await query.message.reply_text("❌ Please select both Gender and Language")
            return

        voice_key = f"{lang}_{gender}"
        voice = VOICE_MAP.get(voice_key)

        if not voice:
            await query.message.reply_text(f"❌ Voice not found for {voice_key}")
            return

        # Show generating message
        msg = await query.message.reply_text("🎙️ Generating audio... ⏳")

        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_path = tmp.name

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate="-10%",     # slightly slower – feels more natural for reels
                pitch="+1Hz"     # very slight lift – sounds clearer
            )

            await communicate.save(audio_path)

            await msg.edit_text("✅ Audio ready!")

            await query.message.reply_audio(
                audio=open(audio_path, "rb"),
                caption=f"Voice: {voice}\nText length: {len(text)} chars",
                title="Reels Voice",
                performer="Edge TTS"
            )

        except edge_tts.exceptions.NoAudioReceived:
            await msg.edit_text("❌ No audio received from server. Try shorter text or different voice.")
        except Exception as e:
            await msg.edit_text(f"❌ Error: {str(e)[:200]}")
        finally:
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass

        # Clean user data after success or failure
        context.user_data.clear()


def main():
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable not set")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))

    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
