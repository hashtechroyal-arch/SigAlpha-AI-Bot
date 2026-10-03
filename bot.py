import os
import asyncio
import threading
from flask import Flask
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Auto - Sabse naya model khud dhundega
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except:
    model = genai.GenerativeModel("models/gemini-1.5-flash")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Live! By Professor Bunti Royal 👑"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Namaste! 🙏 Main SigAlpha AI hoon. Aapka swagat hai!\n\nBy Professor Bunti Royal 👑")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = model.generate_content(f"You are SigAlpha AI, helpful assistant by Professor Bunti Royal. Reply in same language: {update.message.text}")
        await update.message.reply_text(response.text + "\n\nBy Professor Bunti Royal 👑")
    except Exception as e:
        err = str(e).lower()
        if "429" in err or "quota" in err:
            await update.message.reply_text("Arre boss! Itni tezi! 😅 AI ka dimaag garam ho gaya, thanda hone do 2 min! Fir full speed me jawab dunga! 🔥\n\nBy Professor Bunti Royal 👑")
        elif "404" in err or "not found" in err:
            # Agar model ka naam fir badla to 1.5-flash try karo
            try:
                backup_model = genai.GenerativeModel("gemini-flash-latest")
                resp = backup_model.generate_content(update.message.text)
                await update.message.reply_text(resp.text + "\n\nBy Professor Bunti Royal 👑")
            except Exception as e2:
                await update.message.reply_text(f"Model update ho raha hai, 2 min baad try karo! 👑\n\nBy Professor Bunti Royal 👑")
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
