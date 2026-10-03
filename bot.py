import os, asyncio, threading
from flask import Flask
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = Flask(__name__)

@app.route('/')
def home():
    return "SigAlpha Live - Groq Unlimited"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready! By Professor Bunti Royal 👑")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        chat = groq_client.chat.completions.create(
            chat = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": "You are SigAlpha bot made by Professor Bunti Royal. Reply in Hinglish, cool and friendly style."},
        {"role": "user", "content": user_text}
    ]
)
            messages=[
                {"role": "system", "content": "You are SigAlpha bot made by Professor Bunti Royal. Reply in Hinglish, cool and friendly style."},
                {"role": "user", "content": user_text}
            ]
        )
        reply = chat.choices[0].message.content
        await update.message.reply_text(reply + "\n\nBy Professor Bunti Royal 👑")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())
