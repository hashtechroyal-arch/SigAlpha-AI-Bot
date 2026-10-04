import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha V16 AUTO-MODEL 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
GEM_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
GROQ_KEY = (os.getenv("GROQ_API_KEY") or "").strip()

gemini_client = None
groq_client = None

try:
    from google import genai
    if GEM_KEY.startswith("AIza"):
        gemini_client = genai.Client(api_key=GEM_KEY)
        print("NEW GENAI READY")
except Exception as e: print(f"GENAI INIT: {e}")

try:
    from groq import Groq
    if GROQ_KEY:
        groq_client = Groq(api_key=GROQ_KEY)
        print("GROQ READY")
except Exception as e: print(f"GROQ INIT: {e}")

GEMINI_MODELS = ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
GROQ_MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]

async def ask_ai(text):
    if gemini_client:
        for model_name in GEMINI_MODELS:
            try:
                r = gemini_client.models.generate_content(model=model_name, contents=text)
                print(f"GEMINI SUCCESS with {model_name}")
                return r.text + "\n\n- Professor Bunti Royal 👑"
            except Exception as e:
                print(f"GEMINI FAIL {model_name}: {e}")
                continue
    if groq_client:
        for model_name in GROQ_MODELS:
            try:
                c = groq_client.chat.completions.create(model=model_name, messages=[{"role":"user","content":text}], max_tokens=800)
                print(f"GROQ SUCCESS with {model_name}")
                return c.choices[0].message.content + "\n\n- Professor Bunti Royal 👑"
            except Exception as e:
                print(f"GROQ FAIL {model_name}: {e}")
                continue
    return f"Bhai {text} ka jawab: Main fully ready hu! Bol kya help chahiye? 🔥\n\n- Professor Bunti Royal 👑"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Namaste {update.effective_user.first_name} ji 🙏 V16 LIVE hai!\n\n- Professor Bunti Royal 👑")
async def logo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from PIL import Image, ImageDraw, ImageFont
    name = " ".join(context.args) if context.args else "BUNTI"
    img = Image.new('RGB', (1000,400), (10,10,10))
    ImageDraw.Draw(img).text((50,150), name, fill=(255,215,0))
    img.save("/tmp/logo.png")
    await update.message.reply_photo(photo=open("/tmp/logo.png",'rb'), caption=f"{name} logo 👑")
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = await ask_ai(update.message.text)
    await update.message.reply_text(ans)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("logo", logo_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("V16 START")
    app.run_polling()

if __name__ == '__main__': main()
