import os, asyncio, threading, itertools, time
from flask import Flask
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict

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
    for _ in range(len(API_KEYS)):
        try:
            genai.configure(api_key=next(key_cycle))
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = await asyncio.to_thread(model.generate_content, update.message.text)
            await update.message.reply_text(res.text + "\n\nBy Professor Bunti Royal 👑")
            return
        except Exception as e:
            print(f"Key fail: {e}")
            await asyncio.sleep(1)
            continue
    await update.message.reply_text("Bhai 1 min ruk ja, key thandi ho rahi hai...")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def run_bot():
    while True:
        try:
            application = Application.builder().token(BOT_TOKEN).build()
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            await application.bot.delete_webhook(drop_pending_updates=True)
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            print("Polling started - no conflict")
            await asyncio.Event().wait()
        except Conflict as e:
            print(f"Conflict aaya, 5 sec ruk raha hu: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Bot crash: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())
