import os, random, sqlite3
from pyrogram import Client, filters
import google.generativeai as genai
from groq import Groq
from PIL import Image, ImageDraw

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Memory
conn = sqlite3.connect("sigalpha.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS memory (uid INTEGER, msg TEXT)")

START_MSGS = [
    "Professor Ji! SigAlpha Hazir hai! Bolo kya kaam hai? 🔥",
    "Super Brain ON hai Professor! 🧠 Pucho jo puchna hai!",
]

def get_reply(uid, name, text, is_owner):
    who = "Professor Bunti Royal Ji" if is_owner else name
    prompt = f"Tum SigAlpha AI ho. Owner sirf Professor Bunti Royal Ji hai. Sirf unko Professor bulao. Baki ko naam se. Har jawab ke end me 'By Professor Bunti Royal Ji' likhna hai. User: {who} bola: {text}"
    try:
        res = gemini_model.generate_content(prompt)
        ans = res.text
    except:
        try:
            c = groq_client.chat.completions.create(model="llama3-8b-8192", messages=[{"role":"user","content":prompt}])
            ans = c.choices[0].message.content
        except Exception as e:
            ans = f"Thoda network issue hai Professor, fir se bhejo: {e}"
    if "By Professor Bunti Royal Ji" not in ans:
        ans += "\n\nBy Professor Bunti Royal Ji"
    return ans

app = Client("SigAlpha-AI-Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    msg = random.choice(START_MSGS)
    if message.from_user.id!= OWNER_ID:
        msg = msg.replace("Professor Ji", message.from_user.first_name)
    await message.reply(f"{msg}\n\nBy Professor Bunti Royal Ji")

@app.on_message(filters.text)
async def chat(client, message):
    uid = message.from_user.id
    name = message.from_user.first_name
    text = message.text
    is_owner = uid == OWNER_ID

    if ("owner" in text.lower() or "malik" in text.lower()) and not is_owner:
        await message.reply(f"Owner sirf ek hi hai - Professor Bunti Royal Ji! Aap {name} ho.\n\nBy Professor Bunti Royal Ji")
        return

    # Thumbnail command
    if "thumbnail banao" in text.lower():
        title = text.replace("thumbnail banao","").strip() or "SigAlpha"
        img = Image.new('RGB', (1280,720), (15,15,15))
        ImageDraw.Draw(img).text((80,300), title[:40], fill=(255,215,0))
        ImageDraw.Draw(img).text((80,600), "By Professor Bunti Royal Ji", fill=(255,255,255))
        img.save("thumb.png")
        await message.reply_photo("thumb.png", caption=f"Ye lo {name} Thumbnail! 🔥\n\nBy Professor Bunti Royal Ji")
        return

    reply = get_reply(uid, name, text, is_owner)
    await message.reply(reply)

print("SigAlpha Super Brain ON hai... 🧠")
app.run()
