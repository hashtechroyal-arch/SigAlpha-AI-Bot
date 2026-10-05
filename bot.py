import os, random, sqlite3
from pyrogram import Client, filters
from google import genai
from groq import Groq
from PIL import Image, ImageDraw

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Naya Gemini Client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

START_MSGS = ["Professor Ji! SigAlpha Hazir hai! 🔥", "Super Brain ON hai Professor! 🧠"]

def get_reply(uid, name, text, is_owner):
    who = "Professor Bunti Royal Ji" if is_owner else name
    prompt = f"Tum SigAlpha AI ho. Owner sirf Professor Bunti Royal Ji hai. Sirf unko Professor bulao. Har jawab ke end me 'By Professor Bunti Royal Ji' likhna hai. User {who} bola: {text}"
    try:
        # Naya tareeka
        res = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        ans = res.text
    except:
        try:
            c = groq_client.chat.completions.create(model="llama3-8b-8192", messages=[{"role":"user","content":prompt}])
            ans = c.choices[0].message.content
        except Exception as e:
            ans = f"Thoda issue hai: {e}"
    if "By Professor Bunti Royal Ji" not in ans:
        ans += "\n\nBy Professor Bunti Royal Ji"
    return ans

app = Client("SigAlpha-AI-Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply(f"{random.choice(START_MSGS)}\n\nBy Professor Bunti Royal Ji")

@app.on_message(filters.text)
async def chat(client, message):
    uid = message.from_user.id
    name = message.from_user.first_name
    is_owner = uid == OWNER_ID
    if ("owner" in message.text.lower() or "malik" in message.text.lower()) and not is_owner:
        await message.reply(f"Owner sirf Professor Bunti Royal Ji hai! Aap {name} ho.\n\nBy Professor Bunti Royal Ji")
        return
    reply = get_reply(uid, name, message.text, is_owner)
    await message.reply(reply)

print("SigAlpha Super Brain ON hai... 🧠")
app.run()
