import os, random, threading, textwrap, logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

# --- 1. 24 GHANTE LIVE RAKHNE KE LIYE ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha V6 UNLIMITED LIVE! 👑🧠♾️"
threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080))), daemon=True).start()

# --- 2. SETUP ---
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
client = Groq(api_key=GROQ_API_KEY)
user_memory = {}

# --- 3. SUPER BRAIN PROMPT ---
SYSTEM_PROMPT = """
Tu SigAlpha V6 hai. Tujhe Professor Bunti Royal ji ne banaya hai. Tu SUPER POWER BRAIN hai UNLIMITED wala.

Tera Character:
- IZZAT: Kabhi bhi Tu/Tera/Tujhe mat bolna. Hamesha AAP, AAPKA, AAPKO bolna.
- DIL SE BAAT: Tu Dilli ka samajhdaar dost hai. Thoda funny, thoda emotional, thoda gyan wala.
- NO BORING: Short, tez, point to point, emoji ke saath.
- STYLE: ** ka use bilkul mat karna. Sirf CAPS aur EMOJI 🙏 👑 🔥 ✨ 😔 💀 😂
- SIGNATURE: Har jawab ke end me ek line gap deke ye likhna hai: - Professor Bunti Royal 👑
"""

# --- 4. WELCOME MESSAGES ---
OWNER_START = [
    "Namaste 🙏 Professor Bunti Royal ji, Aap kaha chale gaye the? Aap ke bina mein adhura hu 😔",
    "🙏 Professor Bunti Royal ji 👑 Aap aa gaye! Aapke bina ye system suna tha. Aagya dijiye! ✨",
    "👑 Dil se Swagat hai Professor Bunti Royal ji 🙏\n\nAapke bina main kuch bhi nahi hu. Boliye aaj kya dhamaka karna hai? 🔥",
    "Namaste Professor Bunti Royal ji 🙏😔\n\nAapka intezaar tha... Ab mehfil shuru hogi! Bataiye kya seva karu?"
]

def get_guest_welcome(name):
    msgs = [
        f"Namaste 🙏 {name} ji ✨\n\nSwagat hai Aapka! Main SigAlpha V6 hoon - SUPER BRAIN 🧠♾️\n\nMain Aapke liye kya kar sakta hu?\n\n📜 /script - Viral Script\n🎨 /thumbnail - Thumbnail\n💡 /idea - Video Idea\n😂 /roast - Masti wala Roast\n📱 /caption - Caption Hashtag\n\nBataiye Aapko kya chahiye?",
        f"Hello {name} ji! 👑🔥\n\nAapka is Royal Bot par dil se swagat hai!\n\nMain har sawal ka jawab de sakta hu - UNLIMITED! Bas puch ke dekhiye!",
        f"🙏 Namaste {name} ji!\n\nMain SigAlpha hoon, Professor Bunti Royal ji ka SUPER BRAIN AI 🧠\n\nAap ek baar /idea likh ke dekhiye, maza aa jayega!"
    ]
    return random.choice(msgs)

# --- 5. UNLIMITED AI FUNCTION - YAHAN SAB KUCH UNLIMITED HAI ---
async def ask_ai(uid, name, user_text, extra_instruction=""):
    if uid not in user_memory:
        user_memory[uid] = []

    user_memory[uid].append(f"User: {user_text}")

    # UNLIMITED LOGIC: 100 message tak yaad rakhega, uske baad bhi delete nahi karega sirf purane hatayega
    if len(user_memory[uid]) > 100:
        user_memory[uid] = user_memory[uid][-100:]

    history = "\n".join(user_memory[uid][-20:])

    if uid == OWNER_ID:
        name_rule = "User is OWNER, Name = Professor Bunti Royal ji. Use AAP and full respect. He is your creator."
    else:
        name_rule = f"User is Guest, Name = {name} ji. Use AAP and respect. Never call him Professor."

    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    reply = ""
    for model in models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + f"\nRULE: {name_rule}\nEXTRA: {extra_instruction}"},
                    {"role": "user", "content": f"Ab tak ki baat:\n{history}\n\nAbhi ka sawal: {user_text}"}
                ],
                temperature=0.85,
                max_tokens=2048 # UNLIMITED: Pehle 1000 tha ab 2048
            )
            reply = completion.choices[0].message.content
            break
        except Exception as e:
            print(f"Model {model} fail: {e}")
            continue

    if not reply:
        reply = "🙏 Maaf kijiye Professor ji, mera dimaag thoda garam ho gaya hai 😔 Ek baar fir se boliye Aap?"

    user_memory[uid].append(f"Bot: {reply}")
    return reply

# --- 6. COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    user_memory.setdefault(uid, [])
    if uid == OWNER_ID:
        await update.message.reply_text(random.choice(OWNER_START))
    else:
        await update.message.reply_text(get_guest_welcome(name))

async def script_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) or "Mahadev ka Rahasya"
    prompt = "Viral YouTube Shorts ke liye 1 minute ki script likh. Hook bahut tez ho, beech me story, end me subscribe bolne ko. Hindi me."
    reply = await ask_ai(update.effective_user.id, update.effective_user.first_name, topic, extra_instruction=prompt)
    await update.message.reply_text(reply)

async def idea_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "3 viral YouTube video ideas de, har idea ke saath Title bhi de. Trending ho."
    reply = await ask_ai(update.effective_user.id, update.effective_user.first_name, "Viral ideas do", extra_instruction=prompt)
    await update.message.reply_text(reply)

async def roast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "User ko pyaar se funny roast karo, gali mat dena, sirf masti me. Dilli wali language me."
    reply = await ask_ai(update.effective_user.id, update.effective_user.first_name, "Mujhe roast karo", extra_instruction=prompt)
    await update.message.reply_text(reply)

async def caption_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) or "Mahakal"
    prompt = "Is topic ke liye 3 viral Instagram Caption de aur 10 trending hashtag bhi de."
    reply = await ask_ai(update.effective_user.id, update.effective_user.first_name, topic, extra_instruction=prompt)
    await update.message.reply_text(reply)

async def thumbnail_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) or "VIRAL"
    W,H=1280,720
    img=Image.new('RGB',(W,H),(12,12,12))
    d=ImageDraw.Draw(img)
    for i in range(H): d.line([(0,i),(W,i)], fill=(int(12+i*0.4),12,25))
    try: font=ImageFont.truetype("arial.ttf", 85)
    except: font=ImageFont.load_default()
    wrapped = textwrap.fill(text.upper(), 12)
    d.text((70,180), wrapped, font=font, fill=(255,215,0), stroke_width=5, stroke_fill=(0,0,0))
    path=f"/tmp/{update.effective_user.id}.jpg"
    img.save(path)
    await update.message.reply_photo(photo=open(path,'rb'), caption=f"Ye lijiye Aapka thumbnail ready hai! 🔥👑\n\nText: {text}")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    reply = await ask_ai(uid, name, update.message.text)
    await update.message.reply_text(reply)

# --- 7. BOT START ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("script", script_cmd))
    app.add_handler(CommandHandler("idea", idea_cmd))
    app.add_handler(CommandHandler("roast", roast_cmd))
    app.add_handler(CommandHandler("caption", caption_cmd))
    app.add_handler(CommandHandler("thumbnail", thumbnail_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("V6 UNLIMITED SUPER BRAIN LIVE! 🧠♾️👑")
    app.run_polling()

if __name__ == '__main__': main()
