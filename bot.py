import os
import tempfile
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from elevenlabs.client import ElevenLabs
from elevenlabs import save as eleven_save  # to save the audio stream

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Heroku Config Vars lo set chey

# Bunty – Reel Perfect Voice
BUNTY_VOICE_ID = "FZkK3TvQ0pjyDmT8fzIW"

# ----------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🎙️ Reels King Voice Bot 🔥 (v3 Enhanced!)\n\n"
        "Send text (mixed Telugu-English ok!)\n"
        "Select gender + lang → Generate\n\n"
        "Now using Eleven v3 for super emotional & mixed energy!"
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
            InlineKeyboardButton("🎙️ Generate Bunty v3", callback_data="generate")
        ]
    ]

    await update.message.reply_text(
        "Text saved! Pick options:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "gender_m":
        context.user_data["gender"] = "m"
    elif data == "gender_f":
        context.user_data["gender"] = "f"
    elif data == "lang_te":
        context.user_data["lang"] = "te"
    elif data == "lang_en":
        context.user_data["lang"] = "en"

    if data in ("gender_m", "gender_f", "lang_te", "lang_en"):
        gender = context.user_data.get("gender", "?")
        lang = context.user_data.get("lang", "?")
        await query.edit_message_text(
            f"Selected:\nGender: {'Male 👨' if gender == 'm' else 'Female 👩' if gender == 'f' else '—'}\n"
            f"Language: {'Telugu 🇮🇳' if lang == 'te' else 'English 🇺🇸' if lang == 'en' else '—'}\n\n"
            "Change or Generate ↓",
            reply_markup=query.message.reply_markup
        )
        return

    if data == "generate":
        text = context.user_data.get("text")
        gender = context.user_data.get("gender")
        lang = context.user_data.get("lang")

        if not text:
            await query.message.reply_text("❌ Text ledu! Pampu first.")
            return
        if not gender or not lang:
            await query.message.reply_text("❌ Gender + Language select chey.")
            return

        voice_id = BUNTY_VOICE_ID

        msg = await query.message.reply_text("🎙️ Generating Bunty v3 mixed energy... ⏳")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_path = tmp.name

        try:
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

            audio_stream = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_v3",  # ← v3 (alpha) added! Super mixed & expressive
                output_format="mp3_44100_128",
                voice_settings={
                    "stability": 0.3,          # Lower for more emotion/variation in mixed text
                    "similarity_boost": 0.9,
                    "style": 0.8,              # Higher for dramatic reels king vibe
                    "use_speaker_boost": False  # Not supported in v3, so False
                }
            )

            eleven_save(audio_stream, audio_path)

            await msg.edit_text("✅ Bunty v3 ready! 🔥 Mixed ravali super ga!")

            lang_name = "Telugu" if lang == "te" else "English"
            await query.message.reply_audio(
                audio=open(audio_path, "rb"),
                caption=f"🎧 Bunty – Reel Perfect (v3)\nLang: {lang_name} | Gender: {'Male' if gender == 'm' else 'Female'}\nText: {text[:80]}...\nTry tags like [excited] or [laughs] for more fun!"
            )

        except Exception as e:
            error_msg = str(e)[:150]
            await msg.edit_text(f"❌ Error: {error_msg}\n(API key/credits/text check chey or v3 alpha kabatti fallback to v2)")
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

        context.user_data.clear()


def main():
    if not TOKEN:
        print("Error: BOT_TOKEN not set!")
        return
    if not ELEVENLABS_API_KEY:
        print("Error: ELEVENLABS_API_KEY not set!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))

    print("Reels King Bot (v3) starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
