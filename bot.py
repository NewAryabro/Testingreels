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
        "🎙️ Reels King Voice Bot 🔥\n\n"
        "Text pampu (Telugu + English mix ok, tags add cheyochu like [excited])\n"
        "Gender + Lang select → Generate\n\n"
        "Bunty high-energy style lo ready!"
    )

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text.strip()

    keyboard = [
        [InlineKeyboardButton("👨 Male", callback_data="gender_m"),
         InlineKeyboardButton("👩 Female", callback_data="gender_f")],
        [InlineKeyboardButton("🇮🇳 Telugu", callback_data="lang_te"),
         InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🎙️ Generate Bunty", callback_data="generate")]
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
            f"Selected: Gender {'Male' if gender == 'm' else 'Female' if gender == 'f' else '—'} | Lang {'Telugu' if lang == 'te' else 'English' if lang == 'en' else '—'}\nChange or Generate!",
            reply_markup=query.message.reply_markup
        )
        return

    if data == "generate":
        text = context.user_data.get("text")
        gender = context.user_data.get("gender")
        lang = context.user_data.get("lang")

        if not text or not gender or not lang:
            await query.message.reply_text("❌ Complete ga select chey bro!")
            return

        voice_id = BUNTY_VOICE_ID
        msg = await query.message.reply_text("🎙️ Generating Bunty voice... ⏳")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_path = tmp.name

        try:
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

            audio_stream = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",  # Stable & safe for Bunty + mixed
                # model_id="eleven_v3",  # Uncomment if v3 want (alpha, may 422 if voice not supported)
                output_format="mp3_44100_128",
                voice_settings={
                    "stability": 0.4,
                    "similarity_boost": 0.85,
                    "style": 0.7,
                    "use_speaker_boost": True  # v2 lo ok, v3 lo False pettuko if switch
                }
            )

            eleven_save(audio_stream, audio_path)

            await msg.edit_text("✅ Ready bro! 🔥")

            lang_name = "Telugu" if lang == "te" else "English"
            await query.message.reply_audio(
                audio=open(audio_path, "rb"),
                caption=f"🎧 Bunty Reel Perfect\nLang: {lang_name} | Gender: {'Male' if gender == 'm' else 'Female'}\nText: {text[:100]}...\nTip: [excited] [laughs] add chey for more energy!"
            )

        except Exception as e:
            error_detail = str(e)
            try:
                if hasattr(e, 'response') and e.response.json():
                    error_detail += f"\nAPI detail: {e.response.json()}"
            except:
                pass
            await msg.edit_text(f"❌ Error: {error_detail[:300]}\n(v3 try chesthe fallback v2 ki, or text short chey / API key check chey)")

        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

        context.user_data.clear()

def main():
    if not TOKEN or not ELEVENLABS_API_KEY:
        print("Error: Keys missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))

    print("Reels King Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()            await msg.edit_text("✅ Audio ready! 🔥")

            lang_name = "Telugu" if lang == "te" else "English"
            await query.message.reply_audio(
                audio=open(audio_path, "rb"),
                caption=f"🎧 Bunty – Reel Perfect Voice\nLang: {lang_name} | Gender: {'Male' if gender == 'm' else 'Female'}\nText: {text[:100]}...\nMixed ravali super ga!"
            )

        except Exception as e:
            error_detail = str(e)
            try:
                if hasattr(e, 'response') and e.response.json():
                    error_detail += f"\nFull API error: {e.response.json()}"
            except:
                pass
            await msg.edit_text(f"❌ Error: {error_detail[:300]}\n(API key/credits/text check chey or text short chey)")
        finally:
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass

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

    print("Reels King Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
