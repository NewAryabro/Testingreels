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
ELEVENLABS_API_KEY = os.getenv("sk_a67a0580b1482c7c5425a788ec8d5a55afb6f46988c1c2a6")  # Get from https://elevenlabs.io → Profile → API Key

# Bunty – Reel Perfect Voice (perfect for reels king energy)
BUNTY_VOICE_ID = "FZkK3TvQ0pjyDmT8fzIW"

# Optional: You can add more voices later, e.g.
# VOICE_MAP = {
#     "te_m": BUNTY_VOICE_ID,
#     "te_f": "some_female_id",
#     ...
# }
# ----------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🎙️ Reels King Voice Bot 🔥\n\n"
        "Send the text you want in Bunty style!\n"
        "Then select gender + language → Generate\n\n"
        "(Using ElevenLabs Bunty – Reel Perfect Voice)"
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
            InlineKeyboardButton("🎙️ Generate Bunty Voice", callback_data="generate")
        ]
    ]

    await update.message.reply_text(
        "Text saved! Now pick voice options:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Gender & Language selection (stored but Bunty used regardless for now)
    if data == "gender_m":
        context.user_data["gender"] = "m"
    elif data == "gender_f":
        context.user_data["gender"] = "f"
    elif data == "lang_te":
        context.user_data["lang"] = "te"
    elif data == "lang_en":
        context.user_data["lang"] = "en"

    # Feedback on selection (optional UX improvement)
    if data in ("gender_m", "gender_f", "lang_te", "lang_en"):
        gender = context.user_data.get("gender", "?")
        lang = context.user_data.get("lang", "?")
        await query.edit_message_text(
            f"Selected:\nGender: {'Male 👨' if gender == 'm' else 'Female 👩' if gender == 'f' else '—'}\n"
            f"Language: {'Telugu 🇮🇳' if lang == 'te' else 'English 🇺🇸' if lang == 'en' else '—'}\n\n"
            "Change or press Generate ↓",
            reply_markup=query.message.reply_markup
        )
        return

    # ── GENERATE ──
    if data == "generate":
        text = context.user_data.get("text")
        gender = context.user_data.get("gender")
        lang = context.user_data.get("lang")

        if not text:
            await query.message.reply_text("❌ No text! Send some first.")
            return
        if not gender or not lang:
            await query.message.reply_text("❌ Select Gender + Language please")
            return

        # For now we use Bunty for everything – best for reels king vibe
        voice_id = BUNTY_VOICE_ID

        # Show progress
        msg = await query.message.reply_text("🎙️ Generating Bunty Reels King voice... ⏳ (ElevenLabs)")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_path = tmp.name

        try:
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

            audio_stream = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",  # Great for Hindi/Telugu/English mix
                output_format="mp3_44100_128",      # Good quality + size
                voice_settings={
                    "stability": 0.35,              # Lower = more expressive/emotional
                    "similarity_boost": 0.9,
                    "style": 0.75,                  # Higher = more dramatic/reel energy
                    "use_speaker_boost": True
                }
            )

            # Save the stream to file
            eleven_save(audio_stream, audio_path)

            await msg.edit_text("✅ Bunty style ready! 🚀")

            lang_name = "Telugu" if lang == "te" else "English"
            await query.message.reply_audio(
                audio=open(audio_path, "rb"),
                caption=f"🎧 Bunty – Reel Perfect Voice\nLang: {lang_name} | Gender: {'Male' if gender == 'm' else 'Female'}\nText: {text[:100]}..."
            )

        except Exception as e:
            error_msg = str(e)[:150]
            await msg.edit_text(f"❌ Error generating audio:\n{error_msg}\n(Check API key / credits / text length)")
        finally:
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass

        # Reset for next use
        context.user_data.clear()


def main():
    if not TOKEN:
        print("Error: BOT_TOKEN not set in environment!")
        return
    if not ELEVENLABS_API_KEY:
        print("Error: ELEVENLABS_API_KEY not set! Get it from elevenlabs.io")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))

    print("Reels King Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
