import os, requests
from flask import Flask, request
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

def get_reply(name, text, is_owner):
    who = "Professor Bunti Royal Ji" if is_owner else name
    prompt = f"Tum SigAlpha AI ho. Tumhara owner Professor Bunti Royal Ji hai. User {who} ne bola: {text}. Hamesha help karo. Har jawab ke end me 'By Professor Bunti Royal Ji' jarur likho."

    # Groq ka sabse stable model
    try:
        c = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        ans = c.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        ans = f"Namaste {who}! Main SigAlpha hoon, thoda busy tha. Fir se bolo? By Professor Bunti Royal Ji"

    if "By Professor Bunti Royal Ji" not in ans:
        ans += "\n\nBy Professor Bunti Royal Ji"
    return ans

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Send Error: {e}")

@app.route('/')
def home():
    return "SigAlpha Live! By Professor Bunti Royal Ji"

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
                send_msg(chat_id, f"Namaste {name}! SigAlpha ON hai! 🔥 Puchho kuch bhi!\n\nBy Professor Bunti Royal Ji")
            else:
                reply = get_reply(name, text, is_owner)
                send_msg(chat_id, reply)
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
