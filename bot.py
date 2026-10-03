import os
import io
import threading
from flask import Flask
from PIL import Image

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- GROQ AI ---
try:
    from groq import Groq
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    groq_client = None

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 1410150440 # Teri ID

# --- MEMORY ---
user_memory = {}

# --- FLASK FOR RENDER (PORT FIX) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "SigAlpha AI Bot is Live by Bunti Royal 👑"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Flask ko alag thread me chalao
threading.Thread(target=run_flask, daemon=True).start()

# --- TELEGRAM HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        user_memory[user_id] = []
        await update.message.reply_text(f"Namaste 🙏 Professor Bunti Royal! 👑\n\nBot Live hai!\n✅ Memory ON\n✅ White BG ON\n✅ Groq AI ON\n\nID Verified: {OWNER_ID}")
    else:
        await update.message.reply_text("❌ Aap Bunti nahi ho! Access denied.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id!= OWNER_ID:
        await update.message.reply_text("Nakli Bunti! ❌")
        return

    user_text = update.message.text

    # Memory save
    if user_id not in user_memory:
        user_memory[user_id] = []
    user_memory[user_id].append(f"User: {user_text}")
    if len(user_memory[user_id]) > 20:
        user_memory[user_id] = user_memory[user_id][-20:]

    # Memory check command
    if "memory" in user_text.lower() and ("dikha" in user_text.lower() or "show" in user_text.lower()):
        mem_text = "\n".join(user_memory[user_id][-10:]) if user_memory[user_id] else "Memory khali hai"
        await update.message.reply_text(f"🧠 Teri Last Memory:\n\n{mem_text}")
        return

    # Groq AI reply
    if groq_client:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are SigAlpha AI Bot, made by Professor Bunti Royal. Reply in Hinglish, friendly, royal style."},
                    {"role": "user", "content": user_text}
                ],
                model="llama-3.1-8b-instant",
            )
            reply = chat_completion.choices[0].message.content
        except Exception as e:
            reply = f"Haan Professor Bunti! Bolo kya kaam hai? 👑 (AI Error: {e})"
    else:
        reply = f"Samajh gaya Professor Bunti: {user_text} 👑"

    user_memory[user_id].append(f"Bot: {reply}")
    await update.message.reply_text(reply)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id!= OWNER_ID:
        return

    await update.message.reply_text("⏳ Ruko Professor, White Background bana raha hu...")

    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        # Open image
        img = Image.open(io.BytesIO(bytes(photo_bytes))).convert("RGB")

        # Create white background image (Light version - RAM safe)
        # Yahan hum image ko white canvas pe paste kar rahe hain
        final_img = Image.new("RGB", img.size, "WHITE")
        final_img.paste(img, (0, 0))

        # Save to bytes
        bio = io.BytesIO()
        bio.name = "white_bg.jpg"
        final_img.save(bio, "JPEG", quality=95)
        bio.seek(0)

        await update.message.reply_photo(photo=bio, caption="✅ Lo Bunti, White Background Ho Gaya! 👑 (Light Mode)")

    except Exception as e:
        await update.message.reply_text(f"❌ Photo Error: {e}")

def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN nahi mila! Render me Environment Variable add karo.")
        return

    print(f"Starting Bot on Port {os.environ.get('PORT', 10000)}...")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ SigAlpha Bot Started Successfully!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
