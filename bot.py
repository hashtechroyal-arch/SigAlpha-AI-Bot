import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OWNER_NAME = os.environ.get("OWNER_NAME", "Professor Bunti Royal")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

@app.route('/')
def home():
    return "SigAlpha AI Bot is Live! By Professor Bunti Royal 👑"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste! Mai SigAlpha AI hu!\nBy {OWNER_NAME} 👑")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text

        # Owner ka sawal
        if "owner" in user_message.lower() or "malik" in user_message.lower():
            await update.message.reply_text(f"Mere malik / owner ka naam {OWNER_NAME} hai 👑")
            return

        # Normal sawal ke liye Gemini se jawab
        response = model.generate_content(f"You are SigAlpha AI, a helpful assistant. Reply in same language as user. User message: {user_message}")
        await update.message.reply_text(response.text)

    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            await update.message.reply_text("🔥 Bhai AI thoda thak gaya hai! Daily limit full ho gayi, 2 ghante baad aana!\n\nBy Professor Bunti Royal 👑")
        else:
            await update.message.reply_text(f"Error: {e}\n\nBy Professor Bunti Royal 👑")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(run_bot())
