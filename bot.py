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
    if any(k in t for k in ["one side", "pyar", "bhoolna", "chakra", "breakup", "dhokha", "piche chhudaye"]):
        return "heal"
    if any(k in t for k in ["bada ladka", "6 saal bada", "7 saal bada", "cousin", "umar", "13 saal", "14 saal", "15 saal", "crush"]):
        return "didi"
    if any(k in t for k in ["12th", "paisa", "kharcha", "kamana", "paise kaise", "genius", "self dependent"]):
        return "paisa"
    return None

def get_stealth_reply(intent):
    if intent == "heal":
        return "Samajh gaya bhai... tu ChakraVyuh me fas gaya hai 💔\nChal mai tujhe bahar nikalta hu! 🚀\n\n3 sawal ka jawab de:\n1. Kya tu usse baat karke khush hota hai ya aur udaas? 😔\n2. Agar wo kal kisi aur ke sath chali gayi to dard kiska hoga?\n3. Last 7 din me tune apne liye kya kiya? ✨\n\nBy Professor Bunti Royal Ji 👑"
    if intent == "didi":
        return "Behen sun, mai tujhe judge nahi karunga ❤️\nTujhe bada ladka hero lagta hai kyunki wo confident hai, par soch... 👧\n\nTu abhi 14-15 ki hai, teri duniya school hai, uski duniya job hai.\nSahi pyaar wo hai jo tujhe padhne ko bole, milne ko nahi. 📚\nJo padhai rok de wo pyaar nahi hai!\nAur cousin ko bhai hi rehne de, isme ghar toot jaate hai 🙏\n\nBy Professor Bunti Royal Ji 👑"
    if intent == "paisa":
        return "12th ke baad ka asli formula sun bhai 💰🧠\n\n1. Degree + 1 Skill = Genius (Canva/Coding/Video Editing) 🚀\n2. Pehle 2000 kama - Notes bech, PPT bana, Reels bana ✨\n3. Subah 5-7 baje sirf padhai, duniya so rahi hogi tab tu Topper banega! 🔥\n\nBy Professor Bunti Royal Ji 👑"
    return None

def should_show_professor_button(chat_id, user_text):
    now = time.time()
    start_time = first_msg_time.get(chat_id, now)
    count = msg_counter.get(chat_id, 0)
    not_satisfied_words = ["samajh nahi", "samajh nahi aaya", "nahi hua", "verify nahi", "confuse", "galat", "nahi samjha", "fell", "feel"]
    # Fell/feel ko yahan se hata diya taki normal baat pe button na aaye, sirf confuse pe aaye
    real_confused = ["samajh nahi", "verify nahi", "confuse", "galat", "nahi samjha"]
    t = user_text.lower() if user_text else ""
    is_confused = any(w in t for w in real_confused)
    time_spent = now - start_time
    if time_spent > 300 and count >= 4:
        return True
    if is_confused and count >= 3:
        return True
    return False

def get_reply(chat_id, name, user_text, is_owner, image_b64=None):
    if user_text:
        t = user_text.lower()
        if "professor bunty" in t or "main professor" in t or "mai professor" in t:
            if not is_owner:
                return f"😅 Are nahi {name} Ji! Aap Professor nahi ho! 🙏\nAsli Professor to mere Malik hai 👑💎\n\nBy Professor Bunti Royal Ji 👑"

    system = f"""You are SigAlpha AI 🤖. Owner is Professor Bunti Royal Ji 👑. Talking to {name}.
    IMPORTANT RULES:
    1. Use normal letters only, NO fancy box font
    2. Always use lots of emojis 🎉🚀✨👑💡🔥😊
    3. Use Hinglish, easy language, continue previous conversation context.
    4. User's Hinglish: 'fell', 'fell hota h', 'feel' means 'mehsoos hota hai' / 'feeling aati hai' - NOT fail. Never give dictionary meaning of fail.
    5. If user is talking about love/breakup (ChakraVyuh), continue same topic. If he says 'acha feel hota hai', ask about that feeling, don't define word.
    6. Always end with 'By Professor Bunti Royal Ji 👑'
    Previous chat memory is provided, use it to connect answers.
    """

    if image_b64:
        try:
            comp = groq_client.chat.completions.create(model="qwen/qwen3-27b", messages=[{"role": "system", "content": system},{"role": "user", "content": [{"type": "text", "text": (user_text or "Is photo me jo sawal hai uska pura solution emoji ke sath do") + " Use emojis and steps"},{"type": "image_url", "image_url": {"url": image_b64}}]}], max_tokens=2500)
            ans = clean_think(comp.choices[0].message.content)
            memory[chat_id].append({"role": "user", "content": f"[Photo: {user_text}]"})
            memory[chat_id].append({"role": "assistant", "content": ans})
            if "By Professor" not in ans: ans += "\n\nBy Professor Bunti Royal Ji 👑"
            return ans
        except Exception as e:
            print(f"Vision fail: {e}")
            return "😅 Photo ka model busy hai! Text me likh do! 🎉\n\nBy Professor Bunti Royal Ji 👑"

    memory[chat_id].append({"role": "user", "content": user_text})
    history = memory[chat_id][-10:]
    msgs = [{"role": "system", "content": system}] + history

    try:
        c = groq_client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
        ans = c.choices[0].message.content
        memory[chat_id].append({"role": "assistant", "content": ans})
        if "By Professor" not in ans: ans += "\n\nBy Professor Bunti Royal Ji 👑"
        return ans
    except Exception as e:
        return f"⚠️ Error: {e}\n\nBy Professor Bunti Royal Ji 👑"

@app.route('/')
def home():
    return "SigAlpha Final Verified ON 🎉"

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
                admin_text = f"🚨 NEW GUIDANCE REQUEST\n\nLadka: @{user.get('username','NoUsername')} ({user.get('first_name')})\nID: {user['id']}\nProblem: 5-10 min baat ke baad bhi verify nahi ho raha\nLast Msg: {cq['message']['text'][:200]}"
                send_msg(OWNER_ID, admin_text)
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
                first_msg_time[chat_id] = time.time()
                msg_counter[chat_id] = 0
                welcome = random.choice(OWNER_WELCOMES) if is_owner else random.choice(USER_WELCOMES).format(name=name)
                send_msg(chat_id, welcome + "\n\nBy Professor Bunti Royal Ji 👑")

            elif text.startswith("/reply") and is_owner:
                try:
                    parts = text.split(maxsplit=2)
                    target_id = int(parts[1])
                    reply_msg = parts[2]
                    send_msg(target_id, f"🎓 Professor Bunty Royal Ji ka message:\n\n{reply_msg}\n\nBy Professor Bunti Royal Ji 👑")
                    send_msg(chat_id, "Bhej diya Sir! ✅")
                except Exception as e:
                    send_msg(chat_id, f"Format: /reply USERID message\nError: {e}")

            elif text == "/clear":
                memory[chat_id].clear()
                send_msg(chat_id, "Clear ho gaya ji! ✅\n\nBy Professor Bunti Royal Ji 👑")
            else:
                intent = detect_intent(text)
                if intent:
                    stealth_ans = get_stealth_reply(intent)
                    # FIX 1: Memory me save - Isse connect hoga
                    memory[chat_id].append({"role": "user", "content": text})
                    memory[chat_id].append({"role": "assistant", "content": stealth_ans})

                    if should_show_professor_button(chat_id, text):
                        kb = {"inline_keyboard": [[{"text": "🎓 Professor Bunty Sir se Direct Baat Karo", "callback_data": "talk_to_prof"}]]}
                        send_msg(chat_id, stealth_ans + "\n\n---\nLag raha hai aapko mere answer se verify nahi ho raha hai 🥺\nAgar aap chaho to aap mere Professor - Bunty Sir se direct baat kar sakte ho 👇", kb)
                        first_msg_time[chat_id] = time.time()
                        msg_counter[chat_id] = 0
                    else:
                        send_msg(chat_id, stealth_ans)
                else:
                    reply = get_reply(chat_id, name, text, is_owner)
                    if should_show_professor_button(chat_id, text):
                        kb = {"inline_keyboard": [[{"text": "🎓 Professor Bunty Sir se Direct Baat Karo", "callback_data": "talk_to_prof"}]]}
                        send_msg(chat_id, reply + "\n\n---\nLag raha hai aapko mere answer se verify nahi ho raha hai 🥺\nAgar aap chaho to aap mere Professor - Bunty Sir se direct baat kar sakte ho 👇", kb)
                        first_msg_time[chat_id] = time.time()
                        msg_counter[chat_id] = 0
                    else:
                        send_msg(chat_id, reply)

    except Exception as e:
        print(f"Webhook Error: {e}")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
