import os, threading, logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "V11 DEBUG LIVE 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
GROQ_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GEM_KEY = (os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY2") or "").strip()

print(f"KEYS CHECK: BOT={len(BOT_TOKEN)} GROQ={len(GROQ_KEY)} GEM={len(GEM_KEY)}")

gemini_model = None
groq_client = None

try:
    if GEM_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEM_KEY)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        print("GEMINI MODEL READY")
except Exception as e: print(f"GEM INIT FAIL: {e}")

try:
    if GROQ_KEY:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_KEY)
        print("GROQ READY")
except Exception as e: print(f"GROQ INIT FAIL: {e}")

async def ask_ai(text):
    # 1. GEMINI
    if gemini_model:
        try:
            res = gemini_model.generate_content(f"Tu SigAlpha hai, Professor Bunti Royal ka bot hai. Hindi me izzat se jawab de. Sawal: {text}")
            return res.text + "\n\n- Professor Bunti Royal 👑"
        except Exception as e:
            err = str(e)
            print(f"GEMINI FAIL: {err}")
            # Agar API key invalid hai to yahi dikhega
            if "API_KEY_INVALID" in err or "403" in err or "400" in err:
                return f"⚠️ Bhai GEMINI KEY me dikkat hai: {err[:200]}\nNayi key banao aistudio.google.com se\n\n- Professor Bunti Royal 👑"

    # 2. GROQ
    if groq_client:
        try:
            c = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":text}], max_tokens=1000)
            return c.choices[0].message.content + "\n\n- Professor Bunti Royal 👑"
        except Exception as e:
            print(f"GROQ FAIL: {e}")

    return "🙏 Bhai abhi AI thoda thak gaya hai, 30 sec me fir bhejo. Key ka issue hai, Render Logs me GEMINI FAIL dekho\n\n- Professor Bunti Royal 👑"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste {update.effective_user.first_name} ji 🙏 V11 LIVE hai 🔥\n\n- Professor Bunti Royal 👑")
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = await ask_ai(update.message.text)
    await update.message.reply_text(ans)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()

if __name__ == '__main__': main()
