import os
import threading
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
from groq import Groq

# ENV from Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_ID = int(os.getenv("API_ID", "2040"))
API_HASH = os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627")
OWNER_ID = 7443912515

app = Client("SigAlpha", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
flask_app = Flask(__name__)
groq_client = Groq(api_key=GROQ_API_KEY)
user_memory = {}

def get_name(user):
    if user.id == OWNER_ID:
        return "Professor Bunti Royal Ji 👑"
    return user.first_name

@flask_app.route('/')
def home():
    return "SigAlpha Bot Live! Jai Hind"

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

@app.on_message(filters.command("start"))
async def start_cmd(_, m):
    name = get_name(m.from_user)
    txt = f"🫡 Jai Hind {name}! 🇮🇳\n\n🔥 Yo! SigAlpha Yaha Hai - Aapka AI Dost! 🤖\n\n✨ Main Kya Kar Sakta Hu?\n💬 Sawal ka jawab\n🎨 Thumbnail - /thumbnail\n\n👑 Mere Malik: Professor Bunti Royal ✨\n\nBy Professor Bunti Royal 👑"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Owner Kaun Hai?", callback_data="owner")],
        [InlineKeyboardButton("🎨 Thumbnail Banao", callback_data="thumb")]
    ])
    await m.reply_text(txt, reply_markup=kb)

@app.on_callback_query()
async def cb(_, q):
    if q.data == "owner":
        await q.message.reply_text("👑 Mere Malik Professor Bunti Royal hai! Genius Developer 🧠\n\nBy Professor Bunti Royal 👑")
    else:
        await q.message.reply_text("🎨 /thumbnail likho fir title\nEx: /thumbnail Pushpa 2\n\nBy Professor Bunti Royal 👑")

@app.on_message(filters.command("thumbnail"))
async def thumb_cmd(_, m):
    if len(m.command) < 2:
        await m.reply_text("Text to do! Ex: /thumbnail Mera Title")
        return
    text = " ".join(m.command[1:])
    img = Image.new('RGB', (1280, 720), color=(25, 25, 25))
    draw = ImageDraw.Draw(img)
    draw.text((50, 300), text[:30], fill=(255, 255, 255))
    img.save("thumb.jpg")
    await m.reply_photo("thumb.jpg", caption=f"🔥 Thumbnail ready: {text}\n\nBy Professor Bunti Royal 👑")

@app.on_message(filters.text & ~filters.command(["start","thumbnail"]))
async def ai_chat(_, m):
    await app.send_chat_action(m.chat.id, enums.ChatAction.TYPING)
    uid = m.from_user.id
    name = get_name(m.from_user)

    if uid not in user_memory:
        user_memory[uid] = []
    user_memory[uid].append({"role": "user", "content": m.text})
    if len(user_memory[uid]) > 6:
        user_memory[uid] = user_memory[uid][-6:]

        system = f"""You are SigAlpha, a helpful AI assistant.
    Your Owner/Creator is Professor Bunti Royal. If someone asks 'Tera owner kaun hai?' or 'Tumhe kisne banaya?' then say Professor Bunti Royal.
    But for real-world facts like YouTube channels, always give correct real answer.
    Science Magnet YouTube channel is owned by Neeraj Sir (Neeraj Jangid), not by Professor Bunti Royal. It is for Railway exams.
    User name is {name}. Talk in Hinglish friendly. Last line always: By Professor Bunti Royal 👑"""

    try:
        messages = [{"role": "system", "content": system}] + user_memory[uid]
        chat = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        reply = chat.choices[0].message.content
        user_memory[uid].append({"role": "assistant", "content": reply})
        await m.reply_text(reply)
    except Exception as e:
        await m.reply_text(f"Thoda error aaya: {e}\n\nBy Professor Bunti Royal 👑")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app.run()
