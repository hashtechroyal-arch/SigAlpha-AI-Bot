@app.on_message(filters.command("start"))
async def start_cmd(_, m):
    print(f"START from {m.from_user.id}")
    name = get_name(m.from_user)
    txt = f"""🫡 **Jai Hind {name}! 🇮🇳** 🫡

🔥 **Yo! SigAlpha Yaha Hai - Aapka AI Dost!** 🤖

✨ **Main Kya Kar Sakta Hu?**
├─ 💬 Koi bhi sawal ka jawab (Hinglish me)
├─ 🎨 Thumbnail / Banner banana - `/thumbnail`
├─ 🧠 Coding, Study, Life Advice sab kuch!

👑 **Mere Malik:**
**Professor Bunti Royal ✨**
Civil Engineer 👷‍♂️ | Genius Developer 🧠 | SigAlpha Owner

🎯 **Meri Soch:**
> *सफलता का कोई शॉर्टकट नहीं होता, मेहनत ही असली पहचान है!*

👇 **Neeche button dabao aur shuru karo!**

**By Professor Bunti Royal 👑**
"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Owner Kaun Hai?", callback_data="owner")],
        [InlineKeyboardButton("🎨 Thumbnail Banao", callback_data="thumb")]
    ])
    await m.reply_text(txt, reply_markup=kb)
