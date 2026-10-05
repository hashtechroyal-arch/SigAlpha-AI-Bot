import os
import asyncio
from groq import Groq
from pyrogram import Client, filters, enums

# --- CONFIG ---
API_ID = int(os.getenv("API_ID", "12345"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_key")

groq_client = Groq(api_key=GROQ_API_KEY)
app = Client("SigAlphaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_memory = {}

def get_name(user):
    return user.first_name or "Bhai"

@app.on_message(filters.command("start"))
async def start_cmd(_, m):
    await m.reply_text(f"Namaste {get_name(m.from_user)}! 👋 Main SigAlpha hu.\n\nBy Professor Bunti Royal 👑")

@app.on_message(filters.command("thumbnail"))
async def thumb_cmd(_, m):
    await m.reply_text("Thumbnail feature abhi band hai.\n\nBy Professor Bunti Royal 👑")

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

    sys_prompt = f"You are SigAlpha, a helpful AI assistant. Your creator and owner is Professor Bunti Royal. If anyone asks who is your owner or who made you, always say Professor Bunti Royal. For real-world factual questions, give 100% true and correct answer. Real fact: Science Magnet YouTube channel is owned by Neeraj Sir (Neeraj Jangid) who teaches for Railway exams, it is NOT owned by Bunti Royal. The user name is {name}. Talk in friendly Hinglish. Always end your reply with new line: By Professor Bunti Royal 👑"

    try:
        messages = [{"role": "system", "content": sys_prompt}] + user_memory[uid]
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
        await m.reply_text(f"Error: {e}\n\nBy Professor Bunti Royal 👑")

print("Bot Starting...")
app.run()
