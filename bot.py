import os
import threading
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
from groq import Groq

# CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = 7443912515 # Aapki ID

app = Client("SigAlpha", bot_token=BOT_TOKEN, api_id=12345, api_hash="hash")
flask_app = Flask(__name__)
groq_client = Groq(api_key=GROQ_API_KEY)

# MEMORY - Thodi yaad rahega
user_memory = {}

def get_name(user):
    if user.id == OWNER_ID:
        return "Professor Bunti Royal Ji 👑"
    return user.first_name

@flask_app.route('/')
def home():
    return "SigAlpha Bot Live! Jai Hind 🫡"

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

# START - JAI HIND WALA
@app.on_message(filters.command("start"))
async def start_cmd(_, m):
    print(f"START from {m.from_user.id}")
    name = get_name(m.from_user)
    txt = f"""🫡 **Jai Hind {name}! 🇮🇳** 🫡

🔥 **Yo! SigAlpha Yaha Hai - Aapka AI Dost!** 🤖

✨ **Main Kya Kar Sakta Hu?**
├─ 💬 Koi bhi sawal ka jawab (Hinglish me)
├─ 🎨 Thumbnail / Banner banana - `/thumbnail`
├─ 🧠 Coding, Study, Life Advice sab kuch!

👑 **Mere Malik:**
**Professor Bunti Royal ✨**
Civil Engineer 👷‍♂️ | Genius Developer 🧠

🎯 **Meri Soch:**
> *सफलता का कोई शॉर्टकट नहीं होता!*

👇 **Neeche button dabao aur shuru karo!**

**By Professor Bunti Royal 👑**
"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Owner Kaun Hai?", callback_data="owner")],
        [InlineKeyboardButton("🎨 Thumbnail Banao", callback_data="thumb")]
    ])
    await m.reply_text(txt, reply_markup=kb)

@app.on_callback_query()
async def cb(_, q):
    if q.data == "owner":
        await q.message.reply_text("👑 Mere Malik **Professor Bunti Royal** hai! Genius Developer 🧠\n\nBy Professor Bunti Royal 👑")
    elif q.data == "thumb":
        await q.message.reply_text("🎨 `/thumbnail` likho fir title likho\nEx: `/thumbnail Pushpa 2`\n\nBy Professor Bunti Royal 👑")

@app.on_message(filters.command("thumbnail"))
async def thumb_cmd(_, m):
    if len(m.command) < 2:
        await m.reply_text("Text to do! Ex: `/thumbnail Mera Title`")
        return
    text = " ".join(m.command[1:])
    img = Image.new('RGB', (1280, 720), color=(0,0,0))
    draw = ImageDraw.Draw(img)
    draw.text((100, 300), text, fill=(255,255,255))
    img.save("thumb.jpg")
    await m.reply_photo("thumb.jpg", caption=f"🔥 Thumbnail ready for: {text}\n\nBy Professor Bunti Royal 👑")

# AI CHAT WITH MEMORY
@app.on_message(filters.text & ~filters.command(["start","thumbnail"]))
async def ai_chat(_, m):
    await app.send_chat_action(m.chat.id, enums.ChatAction.TYPING)
    uid = m.from_user.id
    name = get_name(m.from_user)

    # Memory manage
    if uid not in user_memory:
        user_memory[uid] = []
    user_memory[uid].append({"role": "user", "content": m.text})
    if len(user_memory[uid]) > 6:
        user_memory[uid] = user_memory[uid][-6:]

    system = f"""You are SigAlpha. Owner is Professor Bunti Royal. If user is owner ({name}) respect him highly.
    Talk in Hinglish friendly. Last line always: By Professor Bunti Royal 👑.
    User name: {name}"""

    try:
        messages = [{"role": "system", "content": system}] + user_memory[uid]
        chat = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7
        )
        reply = chat.choices[0].message.content
        user_memory[uid].append({"role": "assistant", "content": reply})
        await m.reply_text(reply)
    except Exception as e:
        print(e)
        await m.reply_text(f"Error: {e}\n\nBy Professor Bunti Royal 👑")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app.run()
