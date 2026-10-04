import os, random, io, threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# Config from Render Env
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY2 = os.getenv("GEMINI_API_KEY2")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Groq safe
groq_client = None
if os.getenv("GROQ_API_KEY"):
    try:
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    except: groq_client = None

def is_owner(uid): return uid == OWNER_ID

async def ask_ai(text, uid, name):
    is_prof = is_owner(uid)
    prompt = f"""
    You are SigAlpha AI. Creator: Professor Bunti Royal.
    Owner ID is {OWNER_ID}. Owner is ONLY Professor Bunti Royal. Never make anyone else owner.
    If user is owner ({is_prof}), call him 'Professor Bunti Royal Ji 👑' with respect. Else call by name {name}.
    Talk like best friend, friendly, funny, never boring. Use Hinglish if user uses Hindi.
    You have super brain memory. You can help with anything.
    If asked about thumbnail/banner, tell user to use /thumbnail <text>.
    End every answer with line: By Professor Bunti Royal 👑
    User ({name}): {text}
    """
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
            except: genai.configure(api_key=GEMINI_API_KEY)
    if groq_client:
        try:
            c = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}])
            return c.choices[0].message.content
        except: pass
    return "Arre thoda issue aa gaya, ek baar fir se bolo Professor Ji! 😅\n\nBy Professor Bunti Royal 👑"

def make_thumb(text):
    img = Image.new('RGB', (1280,720), color=(12,12,30))
    d = ImageDraw.Draw(img)
    try: f = ImageFont.truetype("DejaVuSans-Bold.ttf", 75)
    except: f = ImageFont.load_default()
    d.rectangle([40,180,1240,560], outline=(255,215,0), width=6)
    d.text((640,360), text[:70], font=f, fill=(255,215,0), anchor="mm", stroke_width=4, stroke_fill=(0,0,0))
    bio = io.BytesIO(); img.save(bio, 'PNG'); bio.seek(0); return bio

app = Client("SigAlphaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

START_LIST = [
    "Main hoon SigAlpha AI 🚀 Aapka Super Dost! Koi bhi sawal pucho!",
    "Namaste! ✨ SigAlpha AI is Live! Thumbnail, Banner, Chat sab karunga!",
    "Yo! SigAlpha Yaha Hai 🔥 Bore hone ka chance hi nahi!"
]

@app.on_message(filters.command("start"))
async def start_cmd(_, m):
    name = "Professor Bunti Royal Ji 👑" if is_owner(m.from_user.id) else m.from_user.first_name
    txt = f"Hello {name}! 👋\n\n{random.choice(START_LIST)}\n\n👑 Owner: Professor Bunti Royal\n\nBy Professor Bunti Royal 👑"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("👑 Owner Kaun Hai?", callback_data="owner")],[InlineKeyboardButton("🎨 Thumbnail Help", callback_data="thumb")]])
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

@app.on_message(filters.text & ~filters.command(["start","thumbnail","thumb","banner"]))
async def chat_cmd(_, m):
    if "owner" in m.text.lower() or "malik" in m.text.lower() or "kisne banaya" in m.text.lower():
        return await m.reply_text("👑 Mera Owner / Creator sirf **Professor Bunti Royal** hai! Wahi mere Malik hain!\n\nBy Professor Bunti Royal 👑")
    await app.send_chat_action(m.chat.id, 1)
    name = "Professor Bunti Royal Ji" if is_owner(m.from_user.id) else m.from_user.first_name
    ans = await ask_ai(m.text, m.from_user.id, name)
    await m.reply_text(ans)

# Web server to keep Render alive
web = Flask(__name__)
@web.route('/')
def home(): return "SigAlpha AI Running - By Professor Bunti Royal 👑"
threading.Thread(target=lambda: web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()

print("SigAlpha AI Starting... By Professor Bunti Royal")
app.run()
