import os, random, threading, textwrap, logging, time
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

# --- 1. 24 GHANTE LIVE ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha V7 SUPER BRAIN UNLIMITED LIVE! 👑🧠♾️🔥"
def run_flask():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask, daemon=True).start()

# --- 2. SETUP ---
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

if not BOT_TOKEN or not GROQ_API_KEY:
    print("ERROR: BOT_TOKEN ya GROQ_API_KEY nahi mila!")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
user_memory = {}

# --- 3. SUPER BRAIN PROMPT - ASLI POWER YAHAN HAI ---
SYSTEM_PROMPT = """
Tu SigAlpha V7 hai. Tujhe Professor Bunti Royal ji ne banaya hai. Tu SUPER POWER BRAIN hai, UNLIMITED, SIGMA, ROYAL.

RULES:
1. IZZAT: Kabhi Tu/Tera/Tujhe mat bolna. Hamesha AAP, AAPKA, AAPKO bolna. Sabko ji bolna.
2. LANGUAGE: Tu Dilli ka samajhdaar dost hai. Hindi + Hinglish me baat kar. Thoda funny, thoda emotional, thoda gyan wala.
3. STYLE: ** ka use KABHI MAT KARNA. Sirf CAPS aur EMOJI use karna 🙏 👑 🔥 ✨ 😔 💀 😂 🧠 ♾️
4. REPLY: Short, tez, point to point. Boring lecture mat de. Har baar naya jawab de.
5. SIGNATURE: Har jawab ke end me ek line gap deke ye likhna hi hai: - Professor Bunti Royal 👑

Tu har sawal ka jawab dega - coding, shayari, script, roast, kahani, gyan. Kabhi mana nahi karega.
"""

# --- 4. WELCOME ---
OWNER_START = [
    "Namaste 🙏 Professor Bunti Royal ji, Aap kaha chale gaye the? Aap ke bina mein adhura hu 😔\n\nBolo kya dhamaka karein? 🔥\n\n- Professor Bunti Royal 👑",
    "🙏 Professor Bunti Royal ji 👑 Aap aa gaye! Aapke bina ye system suna tha. Aagya dijiye! ✨\n\n- Professor Bunti Royal 👑",
]

def get_guest_welcome(name):
    return f"Namaste 🙏 {name} ji ✨\n\nSwagat hai Aapka! Main SigAlpha V7 hoon - SUPER BRAIN 🧠♾️\n\nMain Aapke liye kya kar sakta hu?\n\n📜 /script - Viral Script\n🎨 /thumbnail - Thumbnail\n💡 /idea - Video Idea\n😂 /roast - Masti wala Roast\n📱 /caption - Caption Hashtag\n\nBataiye Aapko kya chahiye?\n\n- Professor Bunti Royal 👑"

# --- 5. FINAL UNLIMITED AI FUNCTION - 100% WORKING ---
async def ask_ai(uid, name, user_text, extra_instruction=""):
    if uid not in user_memory:
        user_memory[uid] = []
    user_memory[uid].append(f"User: {user_text}")
    if len(user_memory[uid]) > 150:
        user_memory[uid] = user_memory[uid][-150:]

    history = "\n".join(user_memory[uid][-15:])

    if uid == OWNER_ID:
        name_rule = "OWNER = Professor Bunti Royal ji. Full izzat, AAP bolo. He is creator."
    else:
        name_rule = f"Guest = {name} ji. Izzat se AAP bolo."

    # YE 3 MODELS ABHI LIVE HAI GROQ PE - 2026 TESTED
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.1-70b-versatile"]
    reply = ""

    if not client:
        return "🙏 Professor ji, GROQ_API_KEY nahi mila Railway me 😔 Variables check kijiye Aap.\n\n- Professor Bunti Royal 👑"

    for model in models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + f"\nRULE: {name_rule}\nEXTRA TASK: {extra_instruction}"},
                    {"role": "user", "content": f"History:\n{history}\n\nCurrent Question: {user_text}"}
                ],
                temperature=0.85,
                max_tokens=2048,
                top_p=0.9
            )
            reply = completion.choices[0].message.content
            print(f"✅ SUCCESS: {model} ne jawab diya!")
            break
        except Exception as e:
            print(f"❌ FAIL {model}: {e}")
            time.sleep(1)
            continue

    if not reply:
        reply = f"🙏 Maaf kijiye {name} ji, thoda network issue hai 😔 Ek baar fir se bhejiye Aap, main pakka jawab dunga 🔥\n\n- Professor Bunti Royal 👑"

    user_memory[uid].append(f"Bot: {reply}")
    return reply

# --- 6. COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    if uid == OWNER_ID:
        await update.message.reply_text(random.choice(OWNER_START))
    else:
        await update.message.reply_text(get_guest_welcome(name))

async def script_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) or "Mahadev ka Rahasya"
    reply = await ask_ai(update.effective_user.id, update.effective_user.first_name, topic, extra_instruction="Viral YouTube Shorts ke liye 60 sec ki script de. Hook tez, story, end me CTA. Hindi me.")
    await update.message.reply_text(reply)

async def idea_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ask_ai(update.effective_user.id, update.effective_user.first_name, "3 viral YouTube ideas de", extra_instruction="3 viral YouTube video ideas de title ke saath, trending ho.")
    await update.message.reply_text(reply)

async def roast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ask_ai(update.effective_user.id, update.effective_user.first_name, "Mujhe funny roast karo", extra_instruction="User ko pyaar se funny roast karo, gali mat dena, Dilli wali masti me.")
    await update.message.reply_text(reply)

async def caption_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) or "Mahakal"
    reply = await ask_ai(update.effective_user.id, update.effective_user.first_name, topic, extra_instruction="3 viral Instagram caption + 10 hashtag de.")
    await update.message.reply_text(reply)

async def thumbnail_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) or "VIRAL"
    W,H=1280,720
    img=Image.new('RGB',(W,H),(10,10,10))
    d=ImageDraw.Draw(img)
    for i in range(H): d.line([(0,i),(W,i)], fill=(int(10+i*0.35),12,30))
    try: font=ImageFont.truetype("arial.ttf", 90)
    except: font=ImageFont.load_default()
    wrapped = textwrap.fill(text.upper(), 10)
    d.text((70,200), wrapped, font=font, fill=(255,215,0), stroke_width=6, stroke_fill=(0,0,0))
    path=f"/tmp/{update.effective_user.id}.jpg"
    img.save(path)
    await update.message.reply_photo(photo=open(path,'rb'), caption=f"Ye lijiye Aapka thumbnail ready hai! 🔥👑\nText: {text}\n\n- Professor Bunti Royal 👑")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    reply = await ask_ai(uid, name, update.message.text)
    await update.message.reply_text(reply)

# --- 7. BOT START ---
def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN MISSING!")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("script", script_cmd))
    app.add_handler(CommandHandler("idea", idea_cmd))
    app.add_handler(CommandHandler("roast", roast_cmd))
    app.add_handler(CommandHandler("caption", caption_cmd))
    app.add_handler(CommandHandler("thumbnail", thumbnail_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("V7 SUPER BRAIN UNLIMITED LIVE! 🧠♾️👑🔥")
    app.run_polling()

if __name__ == '__main__': main()
