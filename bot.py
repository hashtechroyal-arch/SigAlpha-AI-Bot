import os
import asyncio
import threading
import base64
from flask import Flask
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from PIL import Image
from rembg import remove

BOT_TOKEN = os.environ.get("BOT_TOKEN")
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- APNI ID YAHAN DALO @userinfobot se leke ---
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))

app = Flask(__name__)
@app.route('/')
def home():
    return "SigAlpha Final Verified Live"

CHAT_HISTORY = {}
def get_history(user_id):
    if user_id not in CHAT_HISTORY:
        CHAT_HISTORY[user_id] = []
    return CHAT_HISTORY[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid == OWNER_ID:
        await update.message.reply_text(f"Namaste 🙏 Professor Bunti Royal! Kaise ho Aap? 👑\nOwner Verified: {uid}")
    else:
        await update.message.reply_text(f"SigAlpha Ready! 👑\nBy Professor Bunti Royal")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    if not user_text:
        return
    text_lower = user_text.lower()

    # --- FINAL MALIK VERIFICATION ---
    if "malik hu" in text_lower or "i am professor bunti" in text_lower or "mai tumhara malik" in text_lower:
        if user_id!= OWNER_ID:
            await update.message.reply_text(
                "😂 Arre bhai Nakli Bunti spotted! ❌\n"
                "Asli Professor Bunti Royal to mere dil me baste hain, tum fake ho!\n\n"
                "By Professor Bunti Royal 👑"
            )
            return
        else:
            await update.message.reply_text(
                "Namaste 🙏 Professor Bunti Royal! Kaise ho Aap? 👑\n\n"
                "Aapka apna SigAlpha ekdum mast chal raha hai, bas aapke hukam ka intezar hai! "
                "Bataiye Malik, aaj kya dhamaka karna hai? 🔥\n\n"
                "By Professor Bunti Royal 👑"
            )
            return

    # Link check
    if "http" in user_text and ("youtube.com" in user_text or "youtu.be" in user_text or "instagram.com" in user_text):
        await handle_link(update, context)
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    hist = get_history(user_id)
    hist.append({"role": "user", "content": user_text})
    if len(hist) > 12:
        hist.pop(0)

    try:
        system_prompt = f"""
        You are SigAlpha by Professor Bunti Royal.
        OWNER_ID is {OWNER_ID}. Only this ID is real owner.
        You are emotionally intelligent best friend. Detect emotion and use matching emoji: sad=😭🫂❤️ happy=🥳🔥 lonely=🤗.
        Make user feel someone cares. Be desi Hinglish, short, dil se.
        Remember chat history.
        End with 'By Professor Bunti Royal 👑'
        """
        res = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system_prompt}, *hist]
        )
        ans = res.choices[0].message.content
        hist.append({"role": "assistant", "content": ans})
        await update.message.reply_text(ans)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = (update.message.caption or "").lower()
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("input.jpg")

    if "background" in caption or "bg hata" in caption:
        try:
            out = remove(Image.open("input.jpg"))
            out.save("output.png")
            await update.message.reply_photo(photo=open("output.png", "rb"), caption="Background gayab! By Professor Bunti Royal 👑")
        except Exception as e:
            await update.message.reply_text(f"BG Error: {e}")
        return

    try:
        with open("input.jpg", "rb") as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        res = groq_client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "Is photo ka detail Hinglish me bata"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]}]
        )
        await update.message.reply_text(res.choices[0].message.content + "\n\nBy Professor Bunti Royal 👑")
    except Exception as e:
        await update.message.reply_text(f"Photo Error: {e}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    voice_file = await update.message.voice.get_file()
    await voice_file.download_to_drive("voice.ogg")
    try:
        with open("voice.ogg", "rb") as f:
            tr = groq_client.audio.transcriptions.create(file=f, model="whisper-large-v3", language="hi")
        update.message.text = tr.text
        await handle_message(update, context)
    except Exception as e:
        await update.message.reply_text(f"Voice Error: {e}")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Downloading boss... ⏳")
    try:
        ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'video.%(ext)s', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("."):
            if file.startswith("video."):
                await update.message.reply_video(video=open(file, 'rb'), caption="Lo ho gaya! By Professor Bunti Royal 👑")
                os.remove(file)
                break
    except Exception as e:
        await update.message.reply_text(f"Link Error: {e}")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())
