import os, asyncio, threading, itertools
from flask import Flask
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEYS = [os.environ.get("GEMINI_API_KEY"), os.environ.get("GEMINI_API_KEY2")]
API_KEYS = [k for k in API_KEYS if k]
key_cycle = itertools.cycle(API_KEYS)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Live - Bunti Royal"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready! By Professor Bunti Royal 👑")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for _ in range(5):
        try:
            key = next(key_cycle)
            genai.configure(api_key=key)
            # Sabse stable model - ye kabhi band nahi hota
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(update.message.text)
            await update.message.reply_text(response.text + "\n\nBy Professor Bunti Royal 👑")
            return
        except Exception as e:
            print(f"Key failed: {e}") # Render logs me dikhega
            continue
    
    await update.message.reply_text("Bhai 2 min ruk ja, dono key thodi garam ho gayi! 😅\n\nBy Professor Bunti Royal 👑")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.initialize(); await application.start()
    await application.updater.start_polling(); await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(run_bot())
