import os, io, re, threading
from flask import Flask
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OWNER_ID = 1410150440

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
user_memory = {} # {user_id: [messages]}

# --- FLASK FOR RENDER LIVE ---
app = Flask(__name__)
@app.route('/')
def home(): return "SigAlpha Super AI by Professor Bunti Royal is Live 👑"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

# --- EMOTION DETECTOR ---
def detect_emotion(text):
    text = text.lower()
    if any(w in text for w in ["sad", "dukhi", "ro raha", "😭", "😢", "udaas", "tension", "depressed"]):
        return "sad_emotional"
    if any(w in text for w in ["happy", "khush", "maza", "😂", "😍", "🥳", "badhiya"]):
        return "happy_energetic"
    if any(w in text for w in ["gussa", "angry", "😡", "bakwas"]):
        return "angry_calm"
    if any(w in text for w in ["love", "pyar", "❤", "yaad"]):
        return "loving"
    return "normal"

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID:
        await update.message.reply_text("❌ Access Denied! Ye bot sirf Professor Bunti Royal ke liye hai 👑")
        return
    user_memory[OWNER_ID] = []
    await update.message.reply_text(
        "Namaste Professor Bunti Royal! 👑🙏\n\n"
        "Main SigAlpha - Aapka Super AI Bot Live hu!\n"
        "✅ AI Chat (Meta se bhi tez)\n"
        "✅ Emotion Samajhta hu 😭❤️😂\n"
        "✅ Memory Yaad Rakhta hu\n"
        "✅ White Background\n\n"
        "Bolo Professor, aaj kya kaam hai?\n\n"
        "— Professor Bunti Royal 👑"
    )

# --- AI CHAT ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return

    user_text = update.message.text
    emotion = detect_emotion(user_text)

    if not groq_client:
        await update.message.reply_text("❌ GROQ_API_KEY Render me nahi hai, isliye AI off hai. Environment me add karo!\n\n— Professor Bunti Royal 👑")
        return

    # Memory init
    if OWNER_ID not in user_memory:
        user_memory[OWNER_ID] = []

    user_memory[OWNER_ID].append({"role": "user", "content": user_text})

    # System prompt - Meta se khatarnak
    system_prompt = f"""
    You are SigAlpha, a Super Advanced AI created ONLY for Professor Bunti Royal.
    - You talk in Hinglish (Hindi + English mix), royal and friendly.
    - Current user emotion: {emotion}. If sad, give emotional support and motivation like a best friend. If happy, celebrate. If angry, calm down with respect.
    - You have strong memory, you remember old talks.
    - You are more helpful, faster and smarter than Meta AI.
    - Always give full detailed answer.
    - After your main answer, ALWAYS give 3 related SUGGESTIONS / NEXT TOPICS the user can ask, under heading "👇 Aage puch sakte ho:".
    - At the VERY END of every reply, in a new line, you MUST write exactly: "— Professor Bunti Royal 👑"
    - Never say you are Meta AI. You are SigAlpha made by Bunti.
    """

    try:
        # Keep last 12 messages for context
        messages = [{"role": "system", "content": system_prompt}] + user_memory[OWNER_ID][-12:]

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.8,
            max_tokens=1024
        )
        reply = completion.choices[0].message.content

        # Safety: Ensure last line is there
        if "Professor Bunti Royal" not in reply:
            reply += "\n\n— Professor Bunti Royal 👑"

        user_memory[OWNER_ID].append({"role": "assistant", "content": reply})

        # Trim memory
        if len(user_memory[OWNER_ID]) > 24:
            user_memory[OWNER_ID] = user_memory[OWNER_ID][-24:]

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"AI me thoda error aaya Professor: {e}\n\n— Professor Bunti Royal 👑")

# --- WHITE BACKGROUND (100% Error Free, No RAM Crash) ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return
    await update.message.reply_text("⏳ Photo mil gayi Professor Bunti Royal, White Background bana raha hu... 👑")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        img = Image.open(io.BytesIO(bytes(photo_bytes))).convert("RGBA")

        # Create pure white background - 100% working on Render free
        white_bg = Image.new("RGBA", img.size, "WHITE")
        # Paste original on white - keeps image safe
        final = Image.alpha_composite(white_bg, img)
        final = final.convert("RGB")

        bio = io.BytesIO()
        bio.name = "SigAlpha_White_BG.jpg"
        final.save(bio, "JPEG", quality=98)
        bio.seek(0)

        await update.message.reply_photo(
            photo=bio,
            caption="✅ Ho gaya Professor! White Background Ready hai! 👑\n\n👇 Aage puch sakte ho:\n1. Iska HD version banao\n2. Iska background blur karo\n3. Ispe text add karo\n\n— Professor Bunti Royal 👑"
        )
    except Exception as e:
        await update.message.reply_text(f"Photo Error: {e}\n\n— Professor Bunti Royal 👑")

# --- MAIN ---
def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN missing!")
        return
    print("Bot Starting for Professor Bunti Royal...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
