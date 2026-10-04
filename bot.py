import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw
from collections import defaultdict, deque

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha V18 WITH MEMORY 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
GEM_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
GROQ_KEY = (os.getenv("GROQ_API_KEY") or "").strip()

# === MEMORY SYSTEM ===
# Har user ka alag dimaag - last 10 baat yaad rahegi
user_memory = defaultdict(lambda: deque(maxlen=10))

gemini_client = None
groq_client = None
try:
    from google import genai
    if GEM_KEY: gemini_client = genai.Client(api_key=GEM_KEY)
except: pass
try:
    from groq import Groq
    if GROQ_KEY: groq_client = Groq(api_key=GROQ_KEY)
except: pass

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
GROQ_MODELS = ["llama-3.3-70b-versatile", "openai/gpt-oss-20b"]

async def ask_ai(user_id, text):
    SYSTEM = "Tu SigAlpha hai. Malik Professor Bunti Royal hai. Kabhi khud ko OpenAI/Meta/Google mat bolna. Tu user ki pichli baaton ko yaad rakhta hai, uska naam aur context use karta hai. Hindi Hinglish me izzat se jawab de."

    # Pichli baatein nikalo
    history = list(user_memory[user_id])
    history_text = "\n".join([f"User: {u} | Bot: {b}" for u,b in history])

    full_prompt = f"{SYSTEM}\n\nPichli Baatein:\n{history_text}\n\nAb ka Sawal: {text}"

    ans = ""
    if groq_client:
        for m in GROQ_MODELS:
            try:
                msgs = [{"role":"system","content":SYSTEM}]
                for u,b in history:
                    msgs.append({"role":"user","content":u})
                    msgs.append({"role":"assistant","content":b})
                msgs.append({"role":"user","content":text})

                c = groq_client.chat.completions.create(model=m, messages=msgs, max_tokens=800)
                ans = c.choices[0].message.content
                print(f"GROQ SUCCESS {m} with memory {len(history)}")
                break
            except Exception as e:
                print(f"GROQ FAIL {m}: {e}")
                continue

    if not ans and gemini_client:
        for m in GEMINI_MODELS:
            try:
                r = gemini_client.models.generate_content(model=m, contents=full_prompt)
                ans = r.text
                print(f"GEMINI SUCCESS {m}")
                break
            except: continue

    if not ans:
        ans = f"Aapne {text} bola, yaad hai mujhe! Mere malik Professor Bunti Royal hain 👑"

    # Memory me save karo
    user_memory[user_id].append((text, ans))

    return ans + "\n\n- Professor Bunti Royal 👑"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_memory[uid].clear()
    await update.message.reply_text(f"Namaste {update.effective_user.first_name} ji 🙏 Memory reset kar di! Ab sab yaad rahega!\n\n- Professor Bunti Royal 👑")

async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_memory[update.effective_user.id].clear()
    await update.message.reply_text("Memory clear ho gayi! 🧹")

async def logo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args) if context.args else "BUNTI"
    img = Image.new('RGB', (1000,400), (10,10,10))
    ImageDraw.Draw(img).text((50,150), name, fill=(255,215,0))
    img.save("/tmp/logo.png")
    await update.message.reply_photo(photo=open("/tmp/logo.png",'rb'))

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = await ask_ai(update.effective_user.id, update.message.text)
    await update.message.reply_text(ans)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(CommandHandler("logo", logo_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("V18 MEMORY START")
    app.run_polling()
if __name__ == '__main__': main()
