import os, requests
from flask import Flask, request
from google import genai
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

def get_reply(name, text, is_owner):
    who = "Professor Bunti Royal Ji" if is_owner else name
    prompt = f"Tum SigAlpha AI ho. Owner Professor Bunti Royal Ji hai. Har jawab ke end me 'By Professor Bunti Royal Ji' likhna hai. {who}: {text}"
    try:
        res = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        ans = res.text
    except Exception as e:
        # Groq ka NAYA model - purana wala band ho gaya hai
        c = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}]
        )
        ans = c.choices[0].message.content

    if "By Professor Bunti Royal Ji" not in ans:
        ans += "\n\nBy Professor Bunti Royal Ji"
    return ans

def send_msg(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text})

@app.route('/')
def home():
    return "SigAlpha Live! By Professor Bunti Royal Ji"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        name = data["message"]["from"].get("first_name","User")
        is_owner = data["message"]["from"]["id"] == OWNER_ID
        if text == "/start":
            send_msg(chat_id, f"Namaste {name}! SigAlpha ON hai! 🔥\n\nBy Professor Bunti Royal Ji")
        else:
            reply = get_reply(name, text, is_owner)
            send_msg(chat_id, reply)
    return "ok"

if __name__ == "__main__":
    url = os.getenv("RENDER_EXTERNAL_URL")
    if url:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={url}/{BOT_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
