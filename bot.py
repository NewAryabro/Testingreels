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
from elevenlabs import save as eleven_save

# CONFIG
TOKEN = os.getenv("BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

BUNTY_VOICE_ID = "FZkK3TvQ0pjyDmT8fzIW"  # Bunty – Reel Perfect Voice

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🎙️ Reels King Voice Bot 🔥 (v3 Alpha Enhanced!)\n\n"
        "Mixed Telugu-English text pampu (tags add cheyochu like [excited])\n"
        "Gender + Lang select chey → Generate\n\n"
        "v3 lo super emotional & mixed ravali!"
    )

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text.strip()

    keyboard = [
        [InlineKeyboardButton("👨 Male", callback_data="gender_m"),
         InlineKeyboardButton("👩 Female", callback_data="gender_f")],
        [InlineKeyboardButton("🇮🇳 Telugu", callback_data="lang_te"),
         InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🎙️ Generate Bunty v3", callback_data="generate")]
    ]

    await update.message.reply_text("Text saved! Options pick chey:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in ["gender_m", "gender_f"]:
        context.user_data["gender"] = data[-1]
    elif data in ["lang_te", "lang_en"]:
        context.user_data["lang"] = data[-2:]

    if data.startswith(("gender_", "lang_")):
        gender = context.user_data.get("gender", "?")
        lang = context.user_data.get("lang", "?")
        await query.edit_message_text(
            f"Selected: Gender {'Male' if gender == 'm' else 'Female' if gender == 'f' else '—'} | Lang {'Telugu' if lang == 'te' else 'English' if lang == 'en' else '—'}\n\nChange or Generate!",
            reply_markup=query.message.reply_markup
        )
        return

    if data == "generate":
        text = context.user_data.get("text")
        gender = context.user_data.get("gender")
        lang = context.user_data.get("lang")

        if not text or not gender or not lang:
            await query.message.reply_text("❌ Text/Gender/Lang complete ga select chey!")
            return

        voice_id = BUNTY_VOICE_ID
        msg = await query.message.reply_text("🎙️ Bunty v3 mixed energy generating... ⏳ (alpha model)")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_path = tmp.name

        try:
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

            audio_stream = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_v3",  # v3 alpha for mixed & expressive!
                output_format="mp3_44100_128",
                voice_settings={
                    "stability": 0.3,  # low = more variation/emotion
                    "similarity_boost": 0.9,
                    "style": 0.8,      # high = dramatic/reel vibe
                    "use_speaker_boost": False  # v3 lo not supported
                }
            )

            eleven_save(audio_stream, audio_path)

            await msg.edit_text("✅ Bunty v3 ready! Mixed ravali super 🔥")

            lang_name = "Telugu" if lang == "te" else "English"
            await query.message.reply_audio(
                audio=open(audio_path, "rb"),
                caption=f"🎧 Bunty v3 (alpha) | Lang: {lang_name} | Gender: {'Male' if gender == 'm' else 'Female'}\nText: {text[:80]}...\nTip: Add [excited], [laughs], [whispers] for more fun!"
            )

        except Exception as e:
            await msg.edit_text(f"❌ Error: {str(e)[:150]}\n(v3 alpha kabatti inconsistent undochu → fallback to v2 cheyochu)")
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

        context.user_data.clear()

def main():
    if not TOKEN or not ELEVENLABS_API_KEY:
        print("Error: BOT_TOKEN or ELEVENLABS_API_KEY missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))

    print("Reels King Bot (v3 alpha) starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
