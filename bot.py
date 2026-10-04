import os, random, io, threading, asyncio
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
print("Groq Client Ready!")

def is_owner(uid): return uid == OWNER_ID
def get_name(user): return "Professor Bunti Royal Ji 👑" if is_owner(user.id) else user.first_name

def ask_groq_sync(text, name):
    try:
        prompt = f"You are SigAlpha AI by Professor Bunti Royal. Owner ONLY Professor Bunti Royal. Be friendly, Hinglish, funny. User {name}: {text}"
        c = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}])
        return c.choices[0].message.content + "\n\nBy Professor Bunti Royal 👑"
    except Exception as e:
        print(f"Groq Error: {e}")
        return f"Ha {name}! 😊 Mast hu! Aapne '{text}' pucha, thoda detail me batao main full help karunga!\n\nBy Professor Bunti Royal 👑"

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
    txt = f"Hello {name}! 👋\n\nYo! SigAlpha Yaha Hai 🔥\nAapka AI best friend! Koi bhi sawal pucho, maza ayega!\n\n👑 Owner: Professor Bunti Royal ✨\nCivil Engineer 👷‍♂️ | Genius Developer 🧠\n\nMeri Soch: 🎯 सफलता का कोई शॉर्टकट नहीं होता।\n\nBy Professor Bunti Royal 👑"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("👑 Owner Kaun Hai?", callback_data="owner")],[InlineKeyboardButton("🎨 Thumbnail Banao", callback_data="thumb")]])
    await m.reply_text(txt, reply_markup=kb)

@app.on_message(filters.command(["thumbnail","thumb","banner"]))
async def thumb_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("Likho: /thumbnail Pushpa 2 Review")
    bio = make_thumb(m.text.split(None,1)[1])
    await app.send_photo(m.chat.id, bio, caption=f"✅ Thumbnail Ready!\n\nBy Professor Bunti Royal 👑")

@app.on_callback_query()
async def cb(_, q):
    if q.data == "owner":
        await q.message.reply_text("👑 **Mere Malik / Creator** 👑\n\n**Name: Professor Bunti Royal ✨**\n**Civil Engineer 👷‍♂️ | Genius Developer 🧠**\n\nYe ladka dil ka bahut hi acha aur sabka chaheta hai ❤️ Ek sachcha Genius hai!\n\nMeri Soch: 🎯 सफलता का कोई शॉर्टकट नहीं होता।\n\nBy Professor Bunti Royal 👑")
    else:
        await q.message.reply_text("🎨 /thumbnail Aapka Text\n\nBy Professor Bunti Royal 👑")

# --- YE MAIN FIX HAI ---
@app.on_message(filters.private & ~filters.command(["start","thumbnail","thumb","banner"]))
async def chat_cmd(_, m):
    print(f"MSG RECEIVED: {m.text} from {m.from_user.id}")
    low = m.text.lower()
    if "owner kaun" in low or "malik kaun" in low or "kisne banaya" in low or low.strip() in ["owner","malik"]:
        return await m.reply_text("👑 Mera Owner / Creator sirf **Professor Bunti Royal** hai! Wahi mere Malik hain!\n\nBy Professor Bunti Royal 👑")
    try:
        await app.send_chat_action(m.chat.id, 1)
        name = "Professor Bunti Royal Ji" if is_owner(m.from_user.id) else m.from_user.first_name
        # Groq ko alag thread me chalao taki hang na ho
        ans = await asyncio.to_thread(ask_groq_sync, m.text, name)
        print(f"REPLYING: {ans[:50]}")
        await m.reply_text(ans)
    except Exception as e:
        print(f"CHAT ERROR: {e}")
        await m.reply_text(f"Ha {m.from_user.first_name}! Bolo kya help chahiye? 😊\n\nBy Professor Bunti Royal 👑")

web = Flask(__name__)
@web.route('/')
def home(): return "SigAlpha Running"
threading.Thread(target=lambda: web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()

print("SigAlpha AI Starting... By Professor Bunti Royal")
app.run()
