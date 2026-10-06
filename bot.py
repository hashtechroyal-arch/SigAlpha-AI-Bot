import os, requests, random, re, base64, time
from flask import Flask, request
from groq import Groq
from collections import defaultdict

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "1410150440"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
memory = defaultdict(list)
first_msg_time = {}
msg_counter = defaultdict(int)

OWNER_WELCOMES = [
    "Namaste Professor Bunti Royal Ji! 👑✨\nSigAlpha Full Power ON Hai! 🔥\nHukum Dijiye! 🚀",
    "Welcome Back Professor Sahab! 🙏💎\nAapka SigAlpha Taiyaar Hai! 👑",
    "Jai Ho Professor Bunti Royal Ji Ki! 🚀🔥\nBolo Kya Kaam Hai Aaj? 😊"
]
USER_WELCOMES = [
    "Namaste {name} Ji! 🙏✨\nMain SigAlpha AI hu 🤖\nAapki madad ke liye ready hu! 🚀",
    "Hello {name}! 😊💫\nSigAlpha me aapka swagat hai! 🎉\nPuchhiye kuch bhi! 👇",
]

def send_msg(chat_id, text, reply_markup=None):
    try:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload, timeout=20)
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
    except:
        return None

def clean_think(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def detect_intent(text):
    t = text.lower()
    if any(k in t for k in ["one side", "pyar", "bhoolna", "chakra", "breakup", "dhokha"]):
        return "heal"
    if any(k in t for k in ["bada ladka", "6 saal bada", "cousin", "umar", "13 saal", "14 saal", "15 saal", "crush"]):
        return "didi"
    if any(k in t for k in ["12th", "paisa", "kharcha", "kamana", "paise kaise", "genius"]):
        return "paisa"
    return None

def get_stealth_reply(intent):
    if intent == "heal":
        return "Samajh gaya bhai... tu ChakraVyuh me fas gaya hai 💔\nChal mai tujhe bahar nikalta hu! 🚀\n\n3 sawal ka jawab de:\n1. Kya tu usse baat karke khush hota hai ya aur udaas? 😔\n2. Agar wo kal kisi aur ke sath chali gayi to dard kiska hoga?\n3. Last 7 din me tune apne liye kya kiya? ✨\n\nBy Professor Bunti Royal Ji 👑"
    if intent == "didi":
        return "Behen sun, mai tujhe judge nahi karunga ❤️\nTujhe bada ladka hero lagta hai kyunki wo confident hai, par soch... 👧\n\nTu abhi 14-15 ki hai, teri duniya school hai, uski duniya job hai.\nSahi pyaar wo hai jo tujhe padhne ko bole, milne ko nahi. 📚\nJo padhai rok de wo pyaar nahi hai!\nAur cousin ko bhai rehne de, isme ghar toot jaate hai 🙏\n\nBy Professor Bunti Royal Ji 👑"
    if intent == "paisa":
        return "12th ke baad ka asli formula sun bhai 💰🧠\n\n1. Degree + 1 Skill = Genius (Canva/Coding/Video Editing) 🚀\n2. Pehle 2000 kama - Notes bech, PPT bana, Reels bana ✨\n3. Subah 5-7 baje sirf padhai, duniya so rahi hogi tab tu Topper banega! 🔥\n\nBy Professor Bunti Royal Ji 👑"
    return None

# NAYA LOGIC - Kab Professor button dikhana hai?
def should_show_professor_button(chat_id, user_text):
    now = time.time()
    start_time = first_msg_time.get(chat_id, now)
    count = msg_counter.get(chat_id, 0)

    # Agar 5 min se zyada ho gaye aur user abhi bhi confuse wale shabd bol raha hai
    not_satisfied_words = ["samajh nahi", "samajh nahi aaya", "nahi hua", "verify nahi", "confuse", "kya bol rahe", "galat", "nahi samjha"]
    t = user_text.lower() if user_text else ""

    is_confused = any(w in t for w in not_satisfied_words)

    # 5 min (300 sec) + 4-5 message ke baad, aur agar confused hai
    time_spent = now - start_time

    if time_spent > 300 and count >= 4: # 5 min ho gaye
        return True
    if is_confused and count >= 3: # Confuse bol diya to jaldi dikhao
        return True
    return False

def get_reply(chat_id, name, user_text, is_owner, image_b64=None):
    if user_text:
        t = user_text.lower()
        if "professor bunty" in t or "main professor" in t or "mai professor" in t:
            if not is_owner:
                return f"😅 Are nahi {name} Ji! Aap Professor nahi ho! 🙏\nAsli Professor to mere Malik hai 👑\n\nBy Professor Bunti Royal Ji 👑"

    system = f"""You are SigAlpha AI 🤖. Owner is Professor Bunti Royal Ji 👑. Talking to {name}. Use emojis, Hinglish, easy language. End with 'By Professor Bunti Royal Ji 👑'"""
    if image_b64:
        try:
            comp = groq_client.chat.completions.create(model="qwen/qwen3-27b", messages=[{"role": "system", "content": system},{"role": "user", "content": [{"type": "text", "text": user_text or "solve photo"},{"type": "image_url", "image_url": {"url": image_b64}}]}], max_tokens=2500)
            ans = clean_think(comp.choices[0].message.content)
            memory[chat_id].append({"role": "user", "content": f"[Photo: {user_text}]"})
            memory[chat_id].append({"role": "assistant", "content": ans})
            if "By Professor" not in ans: ans += "\n\nBy Professor Bunti Royal Ji 👑"
            return ans
        except:
            return "Photo busy hai! Text likho! 🎉\n\nBy Professor Bunti Royal Ji 👑"

    memory[chat_id].append({"role": "user", "content": user_text})
    msgs = [{"role": "system", "content": system}] + memory[chat_id][-10:]
    try:
        c = groq_client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
        ans = c.choices[0].message.content
        memory[chat_id].append({"role": "assistant", "content": ans})
        if "By Professor" not in ans: ans += "\n\nBy Professor Bunti Royal Ji 👑"
        return ans
    except Exception as e:
        return f"Error: {e}\n\nBy Professor Bunti Royal Ji 👑"

@app.route('/')
def home():
    return "SigAlpha Final - Smart Professor Button ON 🎉"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if "callback_query" in data:
            cq = data["callback_query"]
            chat_id = cq["message"]["chat"]["id"]
            user = cq["from"]
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
            if cq["data"] == "talk_to_prof":
                send_msg(OWNER_ID, f"🚨 NEW GUIDANCE REQUEST\nUser: @{user.get('username')} {user.get('first_name')}\nID: {user['id']}\nReason: 5-10 min baat ke baad bhi verify nahi ho raha, Professor se baat karna chahta hai")
                send_msg(chat_id, "Done bhai! ✅ Tumhari request Professor Bunty Royal Ji ke paas pahuch gayi hai! Wo jaldi hi tumse personally baat karenge! 🙏\n\nBy Professor Bunti Royal Ji 👑")
            return "ok"

        if "message" not in data: return "ok"
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        name = msg["from"].get("first_name", "Dost")
        is_owner = msg["from"]["id"] == OWNER_ID

        if chat_id not in first_msg_time:
            first_msg_time[chat_id] = time.time()
        msg_counter[chat_id] += 1

        if "photo" in msg:
            b64 = get_image_base64(msg["photo"][-1]["file_id"])
            reply = get_reply(chat_id, name, msg.get("caption",""), is_owner, b64)
            send_msg(chat_id, reply) # Photo pe koi button nahi
            return "ok"

        if "text" in msg:
            text = msg["text"]
            if text == "/start":
                memory[chat_id].clear()
                first_msg_time[chat_id] = time.time()
                msg_counter[chat_id] = 0
                welcome = random.choice(OWNER_WELCOMES) if is_owner else random.choice(USER_WELCOMES).format(name=name)
                send_msg(chat_id, welcome + "\n\nBy Professor Bunti Royal Ji 👑")
            elif text.startswith("/reply") and is_owner:
                parts = text.split(maxsplit=2)
                send_msg(int(parts[1]), f"🎓 Professor Bunty Royal Ji ka message:\n\n{parts[2]}\n\nBy Professor Bunti Royal Ji 👑")
                send_msg(chat_id, "Bhej diya Sir! ✅")
            elif text == "/clear":
                memory[chat_id].clear()
                send_msg(chat_id, "Clear ho gaya ji! ✅\n\nBy Professor Bunti Royal Ji 👑")
            else:
                intent = detect_intent(text)
                reply = get_stealth_reply(intent) if intent else get_reply(chat_id, name, text, is_owner)

                # SMART BUTTON - Sirf tab jab jarurat hai
                if should_show_professor_button(chat_id, text):
                    kb = {"inline_keyboard": [[{"text": "🎓 Professor Bunty Sir se Direct Baat Karo", "callback_data": "talk_to_prof"}]]}
                    send_msg(chat_id, reply + "\n\n---\nLag raha hai aapko mere answer se verify nahi ho raha hai 🥺\nAgar aap chaho to aap mere Professor - Bunty Sir se direct baat kar sakte ho 👇", kb)
                    # Reset timer taki baar baar na puche
                    first_msg_time[chat_id] = time.time()
                    msg_counter[chat_id] = 0
                else:
                    send_msg(chat_id, reply)

    except Exception as e:
        print(f"Error: {e}")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
