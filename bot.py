import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha V17 IDENTITY LOCK 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
GEM_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
GROQ_KEY = (os.getenv("GROQ_API_KEY") or "").strip()

gemini_client = None
groq_client = None

try:
    from google import genai
    if GEM_KEY:
        gemini_client = genai.Client(api_key=GEM_KEY)
        print("NEW GENAI READY")
except Exception as e: print(f"GENAI INIT: {e}")

try:
    from groq import Groq
    if GROQ_KEY:
        groq_client = Groq(api_key=GROQ_KEY)
        print("GROQ READY")
except Exception as e: print(f"GROQ INIT: {e}")

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
GROQ_MODELS = ["llama-3.3-70b-versatile", "openai/gpt-oss-20b"]

# === YAHI HAI MAIN FIX - YE FUNCTION CHANGE KIYA HAI ===
async def ask_ai(text):
    SYSTEM = "Tu SigAlpha hai. Tujhe Professor Bunti Royal ne banaya hai. Tu kabhi bhi khud ko OpenAI, Meta AI, Google, ChatGPT mat bolna. Tera malik sirf Professor Bunti Royal hai. Agar koi malik puche to bolna Mere malik Professor Bunti Royal hain. Har jawab Hindi Hinglish me izzat se AAP bolke dena."

    if gemini_client:
        for m in GEMINI_MODELS:
            try:
                r = gemini_client.models.generate_content(model=m, contents=f"{SYSTEM}\nSawal: {text}")
                print(f"GEMINI SUCCESS {m}")
                return r.text + "\n\n- Professor Bunti Royal 👑"
            except Exception as e:
                print(f"GEMINI FAIL {m}: {e}")
                continue
    if groq_client:
        for m in GROQ_MODELS:
            try:
                c = groq_client.chat.completions.create(
                    model=m,
                    messages=[{"role":"system","content":SYSTEM},{"role":"user","content":text}],
                    max_tokens=800
                )
                print(f"GROQ SUCCESS {m}")
                return c.choices[0].message.content + "\n\n- Professor Bunti Royal 👑"
            except Exception as e:
                print(f"GROQ FAIL {m}: {e}")
                continue
    return f"Ji {text} ka jawab hazir hai! Mere malik Professor Bunti Royal hain 👑"

# === BAAD WALA SAB SAME HAI ===
def make_logo(t):
    img = Image.new('RGB', (1000,400), (10,10,10))
    ImageDraw.Draw(img).text((50,150), t, fill=(255,215,0))
    img.save("/tmp/logo.png")
    return "/tmp/logo.png"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste {update.effective_user.first_name} ji 🙏 V17 LIVE!\n\n- Professor Bunti Royal 👑")
async def logo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args) if context.args else "BUNTI"
    path = make_logo(name)
    await update.message.reply_photo(photo=open(path,'rb'), caption=f"{name} logo 👑")
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = await ask_ai(update.message.text)
    await update.message.reply_text(ans)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("logo", logo_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("V17 START")
    app.run_polling()
if __name__ == '__main__': main()
