import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha V12 NEW GENAI LIVE 👑🔥"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
GEM_KEY = (os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY2") or "").strip()
GROQ_KEY = (os.getenv("GROQ_API_KEY") or "").strip()

gemini_client = None
groq_client = None

# NEW GOOGLE GENAI - Yahi ab chalega
try:
    from google import genai
    if GEM_KEY:
        gemini_client = genai.Client(api_key=GEM_KEY)
        print("NEW GENAI READY")
except Exception as e:
    print(f"GENAI INIT FAIL: {e}")

try:
    from groq import Groq
    if GROQ_KEY:
        groq_client = Groq(api_key=GROQ_KEY)
except Exception as e:
    print(f"GROQ INIT FAIL: {e}")

async def ask_ai(text):
    # 1. NEW GEMINI 2.0 FLASH - YE PAKKA CHALEGA
    if gemini_client:
        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Tu SigAlpha hai, Professor Bunti Royal ka bot hai. Hindi Hinglish me izzat se jawab de. Sawal: {text}"
            )
            print("GEMINI 2.0 SUCCESS")
            return response.text + "\n\n- Professor Bunti Royal 👑"
        except Exception as e:
            print(f"GEMINI 2.0 FAIL: {e}")

    # 2. GROQ BACKUP
    if groq_client:
        try:
            c = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":text}], max_tokens=1000)
            return c.choices[0].message.content + "\n\n- Professor Bunti Royal 👑"
        except Exception as e:
            print(f"GROQ FAIL: {e}")

    return "Bhai thoda wait karo, AI restart ho raha hai\n\n- Professor Bunti Royal 👑"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste {update.effective_user.first_name} ji 🙏 V12 LIVE hai 🔥\n\n- Professor Bunti Royal 👑")
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = await ask_ai(update.message.text)
    await update.message.reply_text(ans)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("V12 LIVE!")
    app.run_polling()

if __name__ == '__main__': main()
