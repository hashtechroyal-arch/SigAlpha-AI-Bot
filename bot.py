import os, io, threading, asyncio
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
from groq import Groq

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
print("Groq Client Ready! Key:", GROQ_API_KEY[:10] + "...")

def is_owner(uid): return uid == OWNER_ID
def get_name(user): return "Professor Bunti Royal Ji 👑" if is_owner(user.id) else user.first_name

def ask_groq_sync(text, name):
    try:
        print(f"Asking Groq: {text}")
        c = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role":"user","content":f"You are SigAlpha AI by Professor Bunti Royal. Owner is Professor Bunti Royal. User {name} says: {text}. Reply in Hinglish, helpful."}]
        )
        ans = c.choices[0].message.content
        print(f"Groq Reply: {ans[:100]}")
        return ans + "\n\nBy Professor Bunti Royal 👑"
    except Exception as e:
        print(f"!!! GROQ ERROR!!! {e}")
        return f"Ha {name}! Groq me error aaya: {e}. Par main hu na! '{text}' ke baare me detail me batao?\n\nBy Professor Bunti Royal 👑"

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
    print(f"START from {m.from_user.id}")
    name = get_name(m.from_user)
    txt = f"Hello {name}! 👋\n\nYo! SigAlpha Yaha Hai 🔥\n\n👑 Owner: Professor Bunti Royal ✨"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("👑 Owner Kaun Hai?", callback_data="owner")]])
    await m.reply_text(txt, reply_markup=kb)

@app.on_callback_query()
async def cb(_, q):
    await q.message.reply_text("👑 Mere Malik Professor Bunti Royal hain! ✨")

@app.on_message(filters.private)
async def chat_cmd(_, m):
    if m.text.startswith("/"): return
    print(f"MSG RECEIVED: {m.text} from {m.from_user.id}")
    try:
        name = get_name(m.from_user)
        ans = await asyncio.to_thread(ask_groq_sync, m.text, name)
        await m.reply_text(ans)
    except Exception as e:
        print(f"CHAT ERROR: {e}")
        await m.reply_text(f"Error: {e}")

web = Flask(__name__)
@web.route('/')
def home(): return "SigAlpha Running"
threading.Thread(target=lambda: web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
print("SigAlpha AI Starting... By Professor Bunti Royal")
app.run()
