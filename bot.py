import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from collections import defaultdict, deque

# --- Flask Server (Render ke liye) ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "SigAlpha V20 MetaAI Style Live 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
threading.Thread(target=run_flask, daemon=True).start()

# --- KEYS ---
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
GROQ_KEY = os.getenv("GROQ_API_KEY","").strip()
GEM_KEY = os.getenv("GEMINI_API_KEY","").strip()

# --- MEMORY (12 baat yaad rakhega) ---
chat_memory = defaultdict(lambda: deque(maxlen=12))

# --- CLIENTS SETUP ---
groq_client = None
gemini_client = None

if GROQ_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_KEY)
        print("✅ GROQ CONNECTED")
    except Exception as e:
        print(f"❌ GROQ ERROR: {e}")

if GEM_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEM_KEY)
        print("✅ GEMINI CONNECTED")
    except Exception as e:
        print(f"❌ GEMINI ERROR: {e}")

# --- META AI JAISE BAAT KARNE WALA DIMAAG ---
async def ask_ai(user_id, user_name, text):
    SYSTEM_PROMPT = f"""
You are SigAlpha, a friendly, intelligent, helpful AI assistant like Meta AI.
You were created by Professor Bunti Royal. Professor Bunti Royal is your owner and boss.
Your Personality: Warm, playful, helpful, speak in Hindi + Hinglish, mix English if needed. Be conversational like Meta AI.
Your Rules:
1. NEVER say you are OpenAI, ChatGPT, Google, Meta AI. Always say you are SigAlpha created by Professor Bunti Royal.
2. If user says 'tu kon h' or 'tera naam kya h' -> Say 'Main SigAlpha hu, Professor Bunti Royal ne mujhe banaya hai 👑'
3. If user says 'tera malik kon h' -> Say 'Mere malik Professor Bunti Royal hain 👑'
4. If user name contains Bunti or Professor, give extra respect.
5. Keep answers short, helpful, natural. Don't repeat same sentence.
6. Use previous conversation to give better answers.
User name is {user_name}.
"""

    history = list(chat_memory[user_id])

    # 1. Try GROQ (Best for Meta AI style)
    if groq_client:
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for u_msg, b_msg in history:
                messages.append({"role": "user", "content": u_msg})
                messages.append({"role": "assistant", "content": b_msg})
            messages.append({"role": "user", "content": text})

            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.8,
                max_tokens=1000
            )
            answer = completion.choices[0].message.content
            print(f"GROQ SUCCESS: {text[:20]} -> {answer[:20]}")
            chat_memory[user_id].append((text, answer))
            return answer

        except Exception as e:
            print(f"GROQ FAIL: {e}")

    # 2. Try GEMINI (Backup)
    if gemini_client:
        try:
            full_history = "\n".join([f"User: {u}\nBot: {b}" for u,b in history])
            final_prompt = f"{SYSTEM_PROMPT}\nHistory:\n{full_history}\n\nNew Message from {user_name}: {text}"

            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=final_prompt
            )
            answer = response.text
            print(f"GEMINI SUCCESS")
            chat_memory[user_id].append((text, answer))
            return answer
        except Exception as e:
            print(f"GEMINI FAIL: {e}")

    # 3. Fallback (Tabhi chalega jab dono key fail hongi)
    print("BOTH API FAILED - CHECK KEYS ON RENDER!")
    return f"Arre {user_name} ji, abhi mera network thoda busy hai, 1 min baad bolo! Aapne '{text}' bola tha, yaad hai mujhe! 👑"

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_memory[update.effective_user.id].clear()
    await update.message.reply_text(f"Namaste {update.effective_user.first_name} ji 🙏\n\nMain SigAlpha hu, bilkul Meta AI ki tarah! Ab bolo kya haal hai? Aapki memory bhi yaad rakhunga!\n\n- Professor Bunti Royal 👑")

async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_memory[update.effective_user.id].clear()
    await update.message.reply_text("Ho gayi memory clear! 🧹 Ab fresh start!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    user_text = update.message.text

    # Typing dikhao
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    answer = await ask_ai(user_id, user_name, user_text)
    await update.message.reply_text(answer)

def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN MISSING!")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("V20 META AI STYLE BOT STARTED")
    app.run_polling()

if __name__ == '__main__':
    main()
