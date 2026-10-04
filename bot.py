import os
import random
import json
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import google.generativeai as genai
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIG ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY2 = os.getenv("GEMINI_API_KEY2")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Groq Setup
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Groq init failed, will use Gemini only: {e}")
        groq_client = None

# Memory - Super Brain
USER_MEMORY = {}
CHAT_HISTORY = {}

# Random Start Messages - Har baar change hoga
START_MESSAGES = [
    "Hey! Main hoon SigAlpha AI 🚀\nAapka Super Intelligent Dost!\n\nKuch bhi pucho, koi bhi thumbnail/banner banao - main ready hu!\n\nBy Professor Bunti Royal 👑",
    "Namaste! ✨ SigAlpha AI is Live!\n\nMain har sawal ka jawab de sakta hu, code likh sakta hu, thumbnail bana sakta hu!\n\nBolo kya help chahiye?\n\nBy Professor Bunti Royal 👑",
    "Yo! SigAlpha Yaha Hai 🔥\n\nBore hone ka tension hi nahi! Chatting, Gyan, Masti sab hoga!\n\nBy Professor Bunti Royal 👑",
    "Welcome to Future! 🤖\nMain SigAlpha AI - Aapka Personal AI Assistant\n\nMemory: ON 🧠 | Speed: Unlimited ⚡\n\nBy Professor Bunti Royal 👑"
]

OWNER_REPLIES = [
    "Ji Professor Bunti Royal Ji 👑 Hukum Kariye!",
    "Mere Malik Professor Bunti Royal aa gaye! 🙏 Bataiye kya kaam hai?",
]

# App
app = Client("SigAlphaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def is_owner(user_id):
    return user_id == OWNER_ID

def get_user_name(user):
    if is_owner(user.id):
        return "Professor Bunti Royal 👑"
    return user.first_name or "Dost"

def get_memory(user_id):
    return USER_MEMORY.get(user_id, {})

async def ask_ai(prompt, user_id, user_name):
    memory = get_memory(user_id)
    history = CHAT_HISTORY.get(user_id, [])
