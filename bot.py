import os, requests, random, re
from flask import Flask, request
from groq import Groq
from collections import defaultdict

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
memory = defaultdict(list)

OWNER_WELCOMES = [
    "Namaste Professor Bunti Royal Ji! 👑\nSigAlpha Taiyaar Hai! Hukum Dijiye!",
    "Welcome Back Professor Sahab! 🔥\nAapka SigAlpha Full Power ON Hai!",
    "Jai Ho Professor Bunti Royal Ji Ki! 🚀\nBolo Kya Kaam Hai Aaj?"
]
USER_WELCOMES = [
    "Namaste {name} Ji! 🙏\nMain SigAlpha AI hu - Aapki madad ke liye ready hu!",
    "Hello {name}! ✨\nSigAlpha me aapka swagat hai! Puchhiye kuch bhi!",
    "Hey {name}! 🚀\nMain SigAlpha hu - Aapka Personal AI Assistant!"
]

def send_msg(chat_id, text):
    try:
        # Fancy font ko normal kar do
        text = text.replace("𝗕","B").replace("𝗨","U").replace("𝗡","N").replace("𝗧","T").replace("𝗜","I").replace("𝗥","R").replace("𝗢","O").replace("𝗬","Y").replace("𝗔","A").replace("𝗟","L")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=20)
    except Exception as e:
        print(e)

def get_file_url(file_id):
    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}", timeout=10).json()
        path = r["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{path}"
    except: return None

def clean_think(text):
    # Qwen reasoning model ka <think> hatana
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def get_reply(chat_id, name, user_text, is_owner, image_url=None):
    system = "You are SigAlpha AI. Owner is Professor Bunti Royal Ji. Talk to "+name+". Reply in normal simple Hinglish/English, NO fancy unicode box font, only normal letters. Be helpful, superfast. Always end with 'By Professor Bunti Royal Ji'"

    if image_url:
        try:
            print(f"Trying vision with: {image_url}")
            comp = groq_client.chat.completions.create(
                model="qwen/qwen3-32b", # NEW VISION MODEL
                messages=[
                    {"role": "system", "content": system + " You can see images. Explain photo in detail, solve if question in photo with steps."},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_text or "Is photo ko detail me samjhao aur agar isme sawal hai to pura solution do"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]}
                ],
                max_tokens=2000
            )
            ans = clean_think(comp.choices[0].message.content)
            memory[chat_id].append({"role": "user", "content": f"[Photo: {user_text}]"})
            memory[chat_id].append({"role": "assistant", "content": ans})
            if "By Professor Bunti Royal Ji" not in ans: ans += "\n\nBy Professor Bunti Royal Ji"
            return ans
        except Exception as e:
            print(f"Vision failed: {e}")
            return f"Photo ka analysis fail hua: {e}\nPhir se photo bhejo clear wali.\n\nBy Professor Bunti Royal Ji"

    # TEXT CHAT
    memory[chat_id].append({"role": "user", "content": user_text})
    history = memory[chat_id][-10:]
    msgs = [{"role": "system", "content": system}] + history

    try:
        c = groq_client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
        ans = c.choices[0].message.content
        memory[chat_id].append({"role": "assistant", "content": ans})
        if "By Professor Bunti Royal Ji" not in ans: ans += "\n\nBy Professor Bunti Royal Ji"
        return ans
    except Exception as e:
        print(f"Text Error: {e}")
        return f"Error: {e}\n\nBy Professor Bunti Royal Ji"

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

        if "photo" in msg:
            file_id = msg["photo"][-1]["file_id"]
            caption = msg.get("caption", "")
            img_url = get_file_url(file_id)
            send_msg(chat_id, f"Photo mil gayi {name} ji, analyse kar raha hu... 🔍")
            reply = get_reply(chat_id, name, caption, is_owner, img_url)
            send_msg(chat_id, reply)
            return "ok"

        if "text" in msg:
            text = msg["text"]
            if text == "/start":
                memory[chat_id].clear()
                welcome = random.choice(OWNER_WELCOMES) if is_owner else random.choice(USER_WELCOMES).format(name=name)
                send_msg(chat_id, welcome + "\n\nBy Professor Bunti Royal Ji")
            elif text == "/clear":
                memory[chat_id].clear()
                send_msg(chat_id, "Clear ho gaya ji! ✅\n\nBy Professor Bunti Royal Ji")
            else:
                send_msg(chat_id, get_reply(chat_id, name, text, is_owner))
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
