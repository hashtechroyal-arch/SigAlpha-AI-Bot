import os, random, io, threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# --- CONFIG FROM RENDER ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY2 = os.getenv("GEMINI_API_KEY2")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Groq - Main AI
groq_client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("Groq Connected!")
    except Exception as e:
        print(f"Groq Fail: {e}")

def is_owner(uid):
    return uid == OWNER_ID

def get_name(user):
    return "Professor Bunti Royal Ji 👑" if is_owner(user.id) else user.first_name

START_LIST = [
    "Hey! Main hoon SigAlpha AI 🚀\nAapka Super Intelligent Dost!\nKuch bhi pucho! Thumbnail, coding, life advice sab!",
    "Namaste! ✨ SigAlpha AI Live Hai!\nMain har sawal ka jawab de sakta hu! Bore hone ka tension hi nahi!",
    "Yo! SigAlpha Yaha Hai 🔥\nAapka AI best friend! Koi bhi sawal pucho, maza ayega!"
]

async def ask_ai(text, uid, name):
    prompt = f"You are SigAlpha AI. Creator is Professor Bunti Royal. Owner ID {OWNER_ID}. Owner ONLY Professor Bunti Royal. Never make anyone else owner. Be friendly, helpful, funny, like best friend. Use Hinglish if user uses Hindi. User {name} says: {text}. End with - By Professor Bunti Royal"

    # 1. Groq Try
    if groq_client:
        try:
            c = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}])
            return c.choices[0].message.content
        except:
            try:
                c = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}])
                return c.choices[0].message.content
            except Exception as e:
                print(f"Groq Error: {e}")

    # 2. Gemini Try
    try:
        r = model.generate_content(prompt)
        if r.text: return r.text
    except:
        if GEMINI_API_KEY2:
            try:
                genai.configure(api_key=GEMINI_API_KEY2)
                m2 = genai.GenerativeModel('gemini-1.5-flash')
                r2 = m2.generate_content(prompt)
                genai.configure(api_key=GEMINI_API_KEY)
                if r2.text: return r2.text
            except:
                genai.configure(api_key=GEMINI_API_KEY)

    # 3. Guarantee Reply - Kabhi Fail Nahi
    return f"Ha {name}! 😊 Aapne '{text}' bola! Iske baare me detail me batao main full help karunga!\n\nBy Professor Bunti Royal 👑"

def make_thumb(text):
    img = Image.new('RGB', (1280,720), color=(12,12,30))
    d = ImageDraw.Draw(img)
    try: f = ImageFont.truetype("DejaVuSans-Bold.ttf", 75)
    except: f = ImageFont.load_default()
    d.rectangle([40,180,1240,560], outline=(255,215,0), width=6)
    d.text((640,360), text[:70], font=f, fill=(255,215,0), anchor="mm", stroke_width=4, stroke_fill=(0,0,0))
    bio = io.BytesIO(); img.save(bio, 'PNG'); bio.seek(0); return bio

app = Client("SigAlphaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_cmd(_, m):
    name = get_name(m.from_user)
    welcome = random.choice(START_LIST)
    txt = f"Hello {name}! 👋\n\n{welcome}\n\n👑 Owner: Professor Bunti Royal ✨\nCivil Engineer 👷‍♂️ | Genius Developer 🧠\n\nMeri Soch: 🎯 सफलता का कोई शॉर्टकट नहीं होता।\n\nBy Professor Bunti Royal 👑"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("👑 Owner Kaun Hai?", callback_data="owner")],[InlineKeyboardButton("🎨 Thumbnail Banao", callback_data="thumb")]])
    await m.reply_text(txt, reply_markup=kb)

@app.on_message(filters.command(["thumbnail","thumb","banner"]))
async def thumb_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("Likho: /thumbnail Pushpa 2 Review\n\nBy Professor Bunti Royal 👑")
    bio = make_thumb(m.text.split(None,1)[1])
    await app.send_photo(m.chat.id, bio, caption=f"✅ Thumbnail Ready!\n\nBy Professor Bunti Royal 👑")

@app.on_callback_query()
async def cb(_, q):
    if q.data == "owner":
        await q.message.reply_text("👑 **Mere Malik / Creator** 👑\n\n**Name: Professor Bunti Royal ✨**\n**Civil Engineer 👷‍♂️ | Genius Developer 🧠**\n\nYe ladka dil ka bahut hi acha aur sabka chaheta hai ❤️ Ek sachcha Genius hai!\n\nMeri Soch: 🎯 सफलता का कोई शॉर्टकट नहीं होता।\n\nBy Professor Bunti Royal 👑")
    else:
        await q.message.reply_text("🎨 Thumbnail banane ke liye:\n`/thumbnail Aapka Text`\nEx: `/thumbnail My First Vlog`\n\nBy Professor Bunti Royal 👑")

@app.on_message(filters.text)
async def chat_cmd(_, m):
    if m.text.startswith("/"): return
    low = m.text.lower()
    if "owner kaun" in low or "malik kaun" in low or "kisne banaya" in low or low.strip() in ["owner","malik"]:
        return await m.reply_text("👑 Mera Owner / Creator sirf **Professor Bunti Royal** hai! Wahi mere Malik hain!\n\nBy Professor Bunti Royal 👑")
    await app.send_chat_action(m.chat.id, 1)
    name = "Professor Bunti Royal Ji" if is_owner(m.from_user.id) else m.from_user.first_name
    ans = await ask_ai(m.text, m.from_user.id, name)
    await m.reply_text(ans)

# Web Server for Render
web = Flask(__name__)
@web.route('/')
def home(): return "SigAlpha AI Bot Running - By Professor Bunti Royal 👑"
threading.Thread(target=lambda: web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()

print("SigAlpha AI Starting... By Professor Bunti Royal")
app.run()
