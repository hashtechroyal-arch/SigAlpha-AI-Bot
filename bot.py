import os, io, threading
from flask import Flask
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 1410150440
user_memory = {}

app = Flask(__name__)
@app.route('/')
def home(): return "SigAlpha Bot Live 👑"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        user_memory[OWNER_ID] = []
        await update.message.reply_text("Namaste Professor Bunti! 👑 Bot Live hai!")
    else:
        await update.message.reply_text("Aap Bunti nahi ho!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    txt = update.message.text
    if "memory" in txt.lower():
        await update.message.reply_text("Memory:\n" + "\n".join(user_memory.get(OWNER_ID, [])[-10:]))
        return
    user_memory.setdefault(OWNER_ID, []).append(txt)
    await update.message.reply_text(f"Samajh gaya Professor: {txt}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await update.message.reply_text("White background bana raha hu...")
    f = await update.message.photo[-1].get_file()
    b = await f.download_as_bytearray()
    img = Image.open(io.BytesIO(bytes(b))).convert("RGB")
    final = Image.new("RGB", img.size, "WHITE")
    final.paste(img)
    bio = io.BytesIO()
    bio.name = "white.jpg"
    final.save(bio, "JPEG")
    bio.seek(0)
    await update.message.reply_photo(bio, caption="White BG Done! 👑")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()

if __name__ == "__main__": main()
