import os, requests, json
from flask import Flask, request
from groq import Groq
from collections import defaultdict

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GROQ_KEY = os.getenv("GROQ_API_KEY")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://sigalpha-ai-bot.onrender.com")

groq_client = Groq(api_key=GROQ_KEY)
app = Flask(__name__)

# Brain Memory - Har user ka history
memory = defaultdict(list)

def set_webhook():
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={RENDER_URL}/{BOT_TOKEN}"
        requests.get(url, timeout=10)
        print("Webhook Auto Set!")
    except: pass

def get_reply(chat_id, name, text, is_owner):
    # Memory me add karo
    memory[chat_id].append({"role": "user", "content": text})
    # Sirf last 10 yaad rakho
    history = memory[chat_id][-10:]

    system = f"You are SigAlpha AI, super intelligent, superfast, friendly. Owner is Professor Bunti Royal Ji. You are talking to {name} {'who is Owner' if is_owner else ''}. Reply in Hinglish, helpful, powerful. Always end with 'By Professor Bunti Royal Ji'"

    msgs = [{"role": "system", "content": system}] + history

    try:
        c = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=msgs,
            temperature=0.7
        )
        ans = c.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        return f"Bhai Groq Key me issue hai: {e}\n\nRender > Environment me GROQ_API_KEY sahi dalo (gsk_ se start)\n\nBy Professor Bunti Royal Ji"

    # Memory me bot ka jawab bhi save karo
    memory[chat_id].append({"role": "assistant", "content": ans})

    if "By Professor Bunti Royal Ji" not in ans:
        ans += "\n\nBy Professor Bunti Royal Ji"
    return ans

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(e)

@app.route('/')
def home():
    set_webhook()
    return "SigAlpha Brain ON! By Professor Bunti Royal Ji"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            name = data["message"]["from"].get("first_name","User")
            is_owner = data["message"]["from"]["id"] == OWNER_ID

            if text == "/start":
                memory[chat_id].clear()
                send_msg(chat_id, f"Namaste Professor Bunti Royal Ji! 🔥\n\nMain SigAlpha hu - Superfast Brain Memory ke sath ON hu!\nAb jo bhi puchhoge yaad rakhunga!\n\nBy Professor Bunti Royal Ji")
            elif text == "/clear":
                memory[chat_id].clear()
                send_msg(chat_id, "Memory clear ho gayi Professor Ji!\n\nBy Professor Bunti Royal Ji")
            else:
                reply = get_reply(chat_id, name, text, is_owner)
                send_msg(chat_id, reply)
    except Exception as e:
        print(f"Error: {e}")
    return "ok"

# Auto Webhook on Start
set_webhook()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
