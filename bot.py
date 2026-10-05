import os, requests, random, re, base64
from flask import Flask, request
from groq import Groq
from collections import defaultdict

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
memory = defaultdict(list)

OWNER_WELCOMES = [
    "Namaste Professor Bunti Royal Ji! 👑✨\nSigAlpha Full Power ON Hai! 🔥\nHukum Dijiye! 🚀",
    "Welcome Back Professor Sahab! 🙏💎\nAapka SigAlpha Taiyaar Hai! 👑",
    "Jai Ho Professor Bunti Royal Ji Ki! 🚀🔥\nBolo Kya Kaam Hai Aaj? 😊"
]
USER_WELCOMES = [
    "Namaste {name} Ji! 🙏✨\nMain SigAlpha AI hu 🤖\nAapki madad ke liye ready hu! 🚀",
    "Hello {name}! 😊💫\nSigAlpha me aapka swagat hai! 🎉\nPuchhiye kuch bhi! 👇",
]

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=20)
    except Exception as e:
        print(e)

def get_image_base64(file_id):
    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}", timeout=10).json()
        path = r["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{path}"
        img_data = requests.get(file_url, timeout=15).content
        b64 = base64.b64encode(img_data).decode('utf-8')
        return f"data:image/jpeg;base64,{b64}"
    except Exception as e:
        print(f"Image download fail: {e}")
        return None

def clean_think(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def get_reply(chat_id, name, user_text, is_owner, image_b64=None):
    # 🔐 1. NAKLI PROFESSOR BUNTY PAKADNA
    if user_text:
        t = user_text.lower()
        if "professor bunty" in t or "main professor" in t or "mai professor" in t or "i am professor bunty" in t or "me professor bunty" in t:
            if not is_owner:
                return f"😅 Are nahi {name} Ji! Aap Professor Bunti Royal Ji nahi ho! 🙏\nAsli Professor Bunti Royal Ji to mere Malik hai 👑💎\nAap {name} Ji ho! Batao kya help chahiye? 🚀\n\nBy Professor Bunti Royal Ji 👑"
            else:
                return f"Ji bilkul Professor Bunti Royal Ji! 👑🔥 Hukum Dijiye! 🙏✨\nAap hi to mere Owner ho! 😊\n\nBy Professor Bunti Royal Ji 👑"

    # Emoji wala system prompt
    system = f"""You are SigAlpha AI 🤖. Owner is Professor Bunti Royal Ji 👑.
    Talking to {name}.
    IMPORTANT RULES:
    1. Use normal letters only, NO fancy box font
    2. Always use lots of emojis 🎉🚀✨👑💡🔥😊 to make answer beautiful
    3. Use Hinglish, easy language
    4. If photo has maths puzzle, solve step by step with emoji
    5. Always end with 'By Professor Bunti Royal Ji 👑'
    """

    # 📸 2. PHOTO HANDLE
    if image_b64:
        for model_name in ["qwen/qwen3.6-27b", "qwen/qwen3.8-27b"]:
            try:
                print(f"Trying vision: {model_name}")
                comp = groq_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": [
                            {"type": "text", "text": (user_text or "Is photo me jo sawal hai uska pura solution emoji ke sath do") + " Use emojis and steps"},
                            {"type": "image_url", "image_url": {"url": image_b64}}
                        ]}
                    ],
                    max_tokens=2500
                )
                ans = clean_think(comp.choices[0].message.content)
                memory[chat_id].append({"role": "user", "content": f"[Photo: {user_text}]"})
                memory[chat_id].append({"role": "assistant", "content": ans})
                if "By Professor Bunti Royal Ji" not in ans:
                    ans += "\n\nBy Professor Bunti Royal Ji 👑"
                return ans
            except Exception as e:
                print(f"{model_name} fail: {e}")
                continue
        # Fallback agar vision fail ho
        return "😅 Photo ka model thoda busy hai! Aap text me sawal likh do, main emoji ke sath mast jawab dunga! 🎉\n\nBy Professor Bunti Royal Ji 👑"

    # 💬 3. TEXT HANDLE
    memory[chat_id].append({"role": "user", "content": user_text})
    history = memory[chat_id][-10:]
    msgs = [{"role": "system", "content": system}] + history

    try:
        c = groq_client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
        ans = c.choices[0].message.content
        memory[chat_id].append({"role": "assistant", "content": ans})
        if "By Professor Bunti Royal Ji" not in ans:
            ans += "\n\nBy Professor Bunti Royal Ji 👑"
        return ans
    except Exception as e:
        print(f"Text Error: {e}")
        return f"⚠️ Error: {e}\n\nBy Professor Bunti Royal Ji 👑"

@app.route('/')
def home():
    return "SigAlpha Emoji Live 🎉"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if "message" not in data:
            return "ok"
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        name = msg["from"].get("first_name", "Dost")
        is_owner = msg["from"]["id"] == OWNER_ID

        if "photo" in msg:
            file_id = msg["photo"][-1]["file_id"]
            caption = msg.get("caption", "")
            send_msg(chat_id, f"📸 Photo mil gayi {name} ji! 🔍 Analyse kar raha hu... ✨")
            b64 = get_image_base64(file_id)
            reply = get_reply(chat_id, name, caption, is_owner, b64)
            send_msg(chat_id, reply)
            return "ok"

        if "text" in msg:
            text = msg["text"]
            if text == "/start":
                memory[chat_id].clear()
                welcome = random.choice(OWNER_WELCOMES) if is_owner else random.choice(USER_WELCOMES).format(name=name)
                send_msg(chat_id, welcome + "\n\nBy Professor Bunti Royal Ji 👑")
            elif text == "/clear":
                memory[chat_id].clear()
                send_msg(chat_id, "Clear ho gaya ji! ✅\n\nBy Professor Bunti Royal Ji 👑")
            else:
                send_msg(chat_id, get_reply(chat_id, name, text, is_owner))
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
