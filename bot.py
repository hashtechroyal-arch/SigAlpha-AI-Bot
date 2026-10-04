import os, random, threading, logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import google.generativeai as genai

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha V9 NEVER FAIL LIVE! 👑🧠♾️🔥"
def run_flask():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask, daemon=True).start()

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY2 = os.getenv("GEMINI_API_KEY2")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
gemini_keys = [k for k in [GEMINI_API_KEY, GEMINI_API_KEY2] if k]
if gemini_keys:
    genai.configure(api_key=gemini_keys[0])

user_memory = {}
SYSTEM_PROMPT = "Tu SigAlpha V9 hai. Professor Bunti Royal ji ka banaya SUPER BRAIN hai. Tu Hindi + Hinglish me izzat se AAP karke baat karta hai. Kabhi ** ka use mat karna. Har jawab ke end me ye line likhna: - Professor Bunti Royal 👑"

async def ask_ai(uid, name, text):
    if uid not in user_memory: user_memory[uid]=[]
    user_memory[uid].append(f"User: {text}")
    if len(user_memory[uid])>150: user_memory[uid]=user_memory[uid][-150:]
    hist = "\n".join(user_memory[uid][-12:])
    full_prompt = f"{SYSTEM_PROMPT}\nHistory:{hist}\nUser Sawal:{text}\nJawab Hindi me do:"

    # 1. GROQ TRY
    if client:
        for model in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "qwen-2.5-32b"]:
            try:
                c = client.chat.completions.create(model=model, messages=[{"role":"user","content":full_prompt}], max_tokens=2000, temperature=0.8)
                ans = c.choices[0].message.content
                user_memory[uid].append(f"Bot:{ans}")
                print(f"GROQ OK {model}")
                return ans
            except Exception as e:
                print(f"GROQ FAIL {model}: {e}")
                continue

    # 2. GEMINI TRY - YE PAKKA CHALEGA
    for key in gemini_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(full_prompt)
            ans = resp.text
            user_memory[uid].append(f"Bot:{ans}")
            print(f"GEMINI OK with key {key[:10]}")
            return ans
        except Exception as e:
            print(f"GEMINI FAIL key {key[:10]}: {e}")
            continue

    return f"🙏 Maaf kijiye {name} ji, thoda server busy hai 😔 30 sec baad fir bhejiye Aap, main pakka jawab dunga 🔥\n\n- Professor Bunti Royal 👑"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste 🙏 {update.effective_user.first_name} ji 👑\n\nSigAlpha V9 SUPER BRAIN LIVE ho gaya 🧠♾️🔥\nAb bolo kya karna hai?\n\n- Professor Bunti Royal 👑")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_memory[update.effective_user.id]=[]
    await update.message.reply_text("Memory clear ho gayi ji 🧹♾️\n\n- Professor Bunti Royal 👑")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = await ask_ai(update.effective_user.id, update.effective_user.first_name, update.message.text)
    await update.message.reply_text(ans)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("V9 NEVER FAIL LIVE!")
    app.run_polling()

if __name__ == '__main__': main()
