import os, requests
from flask import Flask, request
from google import genai
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_KEY)
groq_client = Groq(api_key=GROQ_KEY)

app = Flask(__name__)

def get_reply(name, text, is_owner):
    who = "Professor Bunti Royal Ji" if is_owner else name
    prompt = f"Tum SigAlpha AI ho. Owner Professor Bunti Royal Ji hai. Har jawab ke end me 'By Professor Bunti Royal Ji' likho. {who}: {text}"
    try:
        res = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        ans = res.text
    except:
        try:
            c = groq_client.chat.completions.create(model="llama3-8b-8192", messages=[{"role":"user","content":prompt}])
            ans = c.choices[0].message.content
        except Exception as e:
            ans = f"Error: {e}"
    if "By Professor Bunti Royal Ji" not in ans:
        ans += "\n\nBy Professor Bunti Royal Ji"
    return ans

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route('/')
def home():
    return "SigAlpha AI Live! By Professor Bunti Royal Ji"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        user_id = data["message"]["from"]["id"]
        name = data["message"]["from"].get("first_name","User")
        is_owner = user_id == OWNER_ID

        if text == "/start":
            send_message(chat_id, f"Namaste {name}! SigAlpha ON hai! 🔥\n\nBy Professor Bunti Royal Ji")
        else:
            if ("owner" in text.lower() or "malik" in text.lower()) and not is_owner:
                send_message(chat_id, f"Owner sirf Professor Bunti Royal Ji hai! Aap {name} ho.\n\nBy Professor Bunti Royal Ji")
            else:
                reply = get_reply(name, text, is_owner)
                send_message(chat_id, reply)
    return "ok"

if __name__ == "__main__":
    # Webhook set karo
    render_url = os.getenv("RENDER_EXTERNAL_URL") # Render ye khud deta hai
    if render_url:
        webhook_url = f"{render_url}/{BOT_TOKEN}"
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
        print(f"Webhook set to {webhook_url}")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
