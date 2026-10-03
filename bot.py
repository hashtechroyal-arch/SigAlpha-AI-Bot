import os
import threading
from flask import Flask
from PIL import Image
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rembg import remove

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 1410150440

# MEMORY DICT
user_memory = {}

app = Flask(__name__)
@app.route('/')
def hello(): return "SigAlpha Bot is Live by Bunti Royal 👑"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        user_memory[OWNER_ID] = []
        await update.message.reply_text(f"Namaste 🙏 Professor Bunti Royal! Kaise ho Aap? 👑\nMemory Clear Kar Di!\nOwner Verified: {OWNER_ID}")
    else:
        await update.message.reply_text("Aap Bunti nahi ho!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID:
        await update.message.reply_text("Nakli Bunti! ❌")
        return

    uid = update.effective_user.id
    if uid not in user_memory: user_memory[uid] = []
    user_memory[uid].append(f"User: {update.message.text}")
    if len(user_memory[uid]) > 10: user_memory[uid] = user_memory[uid][-10:]

    text = update.message.text.lower()
    if "memory" in text:
        mem = "\n".join(user_memory[uid]) if user_memory[uid] else "Khali hai"
        await update.message.reply_text(f"🧠 Teri Memory:\n{mem}")
        return

    if "malik" in text or "hello" in text or "hlo" in text:
        reply = "Haan Professor Bunti! Bolo kya kaam hai? 👑"
    else:
        reply = f"Samajh gaya Professor: {update.message.text}"

    user_memory[uid].append(f"Bot: {reply}")
    await update.message.reply_text(reply)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return
    await update.message.reply_text("⏳ Ruko Professor, background white kar raha hu...")
    try:
        photo_file = await update.message.photo[-1].get_file()
        input_bytes = await photo_file.download_as_bytearray()
        output_bytes = remove(bytes(input_bytes))
        no_bg_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        white_bg = Image.new("RGBA", no_bg_img.size, "WHITE")
        final_img = Image.alpha_composite(white_bg, no_bg_img).convert("RGB")
        bio = io.BytesIO()
        bio.name = "white_bg.jpg"
        final_img.save(bio, "JPEG")
        bio.seek(0)
        await update.message.reply_photo(photo=bio, caption="✅ Lo Bunti, White Background Ho Gaya! 👑")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    if not BOT_TOKEN: return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("SigAlpha Bot Started with Memory...")
    application.run_polling()

if __name__ == "__main__":
    main()
