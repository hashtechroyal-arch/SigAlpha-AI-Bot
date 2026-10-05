import os, requests, random
from flask import Flask, request
from groq import Groq
from collections import defaultdict

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
memory = defaultdict(list)

# /start ke liye gajab welcome - har baar change
OWNER_WELCOMES = [
    "Namaste Professor Bunti Royal Ji! 👑\n\nSigAlpha Taiyaar Hai! Hukum Dijiye!",
    "Welcome Back Professor Sahab! 🔥\n\nAapka SigAlpha Full Power ON Hai!",
    "Jai Ho Professor Bunti Royal Ji Ki! 🚀\n\nBolo Kya Kaam Hai Aaj?",
    "Professor Ji Aa Gaye! 👑💎\n\nSigAlpha Aapki Seva Me Hazir Hai!"
]

USER_WELCOMES = [
    "Namaste {name} Ji! 🙏\n\nMain SigAlpha AI hu - Aapki madad ke liye ready hu!",
    "Hello {name}! ✨\n\nSigAlpha me aapka swagat hai! Puchhiye kuch bhi!",
    "Hey {name}! 🚀\n\nMain SigAlpha hu - Aapka Personal AI Assistant!",
    "Welcome {name} Ji! 💫\n\nSigAlpha ON hai, Bolo kya help chahiye?"
]

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=15)
    except: pass

def get_file_url(file_id):
    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
        path = r["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{path}"
    except: return None

def get_reply(chat_id, name, user_text, is_owner, image_url=None):
    if image_url:
        # PHOTO WALA BRAIN - Vision Model
        try:
            comp = groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": f"You are SigAlpha AI. Owner is Professor Bunti Royal Ji. Talking to {name}. Explain photo in detail, solve question in photo in Hinglish with steps. End with 'By Professor Bunti Royal Ji'"},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_text or "Is photo ko detail me samjhao aur iska solution do"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]}
                ]
            )
            ans = comp.choices[0].message.content
            memory[chat_id].append({"role": "user", "content": f"[Photo bheji: {user_text}]"})
            memory[chat_id].append({"role": "assistant", "content": ans})
            if "By Professor Bunti Royal Ji" not in ans: ans += "\n\nBy Professor Bunti Royal Ji"
            return ans
        except Exception as e:
            print(f"Vision Error: {e}")

    # NORMAL CHAT - Memory ke sath
    memory[chat_id].append({"role": "user", "content": user_text})
    history = memory[chat_id][-12:]

    system = f"You are SigAlpha AI. Owner is Professor Bunti Royal Ji. Talking to {name} {'(Owner)' if is_owner else ''}. Reply superfast, helpful, in Hinglish. Don't mention memory. End with 'By Professor Bunti Royal Ji'"

    msgs = [{"role": "system", "content": system}] + history
    try:
        c = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=msgs
        )
        ans = c.choices[0].message.content
        memory[chat_id].append({"role": "assistant", "content": ans})
        if "By Professor Bunti Royal Ji" not in ans: ans += "\n\nBy Professor Bunti Royal Ji"
        return ans
    except Exception as e:
        print(e)
        return f"Thoda technical issue hai bhai: {e}\n\nBy Professor Bunti Royal Ji"

@app.route('/')
def home(): return "SigAlpha Final Live"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if "message" not in data: return "ok"
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        name = msg["from"].get("first_name","Dost")
        is_owner = msg["from"]["id"] == OWNER_ID

        # 1. PHOTO HANDLE
        if "photo" in msg:
            file_id = msg["photo"][-1]["file_id"] # sabse badi quality
            caption = msg.get("caption", "")
            send_msg(chat_id, f"Photo mil gayi {name} ji, analyse kar raha hu... 🔍")
            img_url = get_file_url(file_id)
            reply = get_reply(chat_id, name, caption, is_owner, img_url)
            send_msg(chat_id, reply)
            return "ok"

        # 2. TEXT HANDLE
        if "text" in msg:
            text = msg["text"]
            if text == "/start":
                memory[chat_id].clear()
                if is_owner:
                    welcome = random.choice(OWNER_WELCOMES)
                else:
                    welcome = random.choice(USER_WELCOMES).format(name=name)
                send_msg(chat_id, welcome + "\n\nBy Professor Bunti Royal Ji")
            elif text == "/clear":
                memory[chat_id].clear()
                send_msg(chat_id, "Clear ho gaya ji! ✅\n\nBy Professor Bunti Royal Ji")
            else:
                reply = get_reply(chat_id, name, text, is_owner)
                send_msg(chat_id, reply)

    except Exception as e:
        print(f"Webhook Error: {e}")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
