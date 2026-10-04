import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from collections import defaultdict, deque
from openai import OpenAI

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha MEGA GROK BOT LIVE 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
OR_KEY = os.getenv("GROQ_API_KEY","").strip()
client = OpenAI(api_key=OR_KEY, base_url="https://openrouter.ai/api/v1")
memory = defaultdict(lambda: deque(maxlen=15))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste {update.effective_user.first_name}! 👑\nMain hu SigAlpha MEGA BOT - Grok Free wala!\nBolo kya chahiye?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        msgs = [{"role":"system","content":f"You are SigAlpha MEGA BOT created by Professor Bunti Royal. You are super intelligent like Grok, witty, savage, helpful. You know everything. Speak in Hindi Hinglish mix. User: {update.effective_user.first_name}"}]
        for u,b in list(memory[uid]):
            msgs.append({"role":"user","content":u})
            msgs.append({"role":"assistant","content":b})
        msgs.append({"role":"user","content":update.message.text})
        r = client.chat.completions.create(model="x-ai/grok-3-mini:free", messages=msgs, max_tokens=1000)
        ans = r.choices[0].message.content
        memory[uid].append((update.message.text, ans))
        await update.message.reply_text(ans)
    except Exception as e:
        await update.message.reply_text(f"Thoda wait karo Professor ji, overload hai: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("MEGA BOT STARTED")
    app.run_polling()
if __name__ == '__main__': main()
