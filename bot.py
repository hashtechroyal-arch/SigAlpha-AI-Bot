import os
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OWNER_NAME = "Professor Bunti Royal"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-3.8-flash")

app = Flask(__name__)

@app.route('/')
def home():
    return "SigAlpha AI Bot is Running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 SigAlpha AI Bot Ready!\nMai All-Rounder hu - Koi bhi sawal pucho!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    user_lower = user_msg.lower()
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Check agar owner ke baare me pucha hai
        owner_keywords = ["owner", "malik", "kisne banaya", "kisne bnaya", "banaya kisne", "creator", "who made you", "who created", "tumhe kisne banaya", "aapko kisne banaya"]
        
        if any(word in user_lower for word in owner_keywords):
            await update.message.reply_text(f"Mere malik / owner ka naam {OWNER_NAME} hai 👑")
            return

        # Normal sawal ke liye Gemini se jawab
        response = model.generate_content(f"You are SigAlpha AI, a helpful assistant. Reply in same language as user. User message: {user_msg}")
        await update.message.reply_text(response.text)
        
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
