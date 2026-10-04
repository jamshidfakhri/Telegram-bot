import telebot
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from langdetect import detect, DetectorFactory
from openai import OpenAI

DetectorFactory.seed = 0

TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL_NAME = "google/gemma-2-9b-it:free"

bot = telebot.TeleBot(TOKEN)

user_histories = {}

def get_ai_response(user_id, user_message, user_lang):
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    user_histories[user_id].append({"role": "user", "content": user_message})
    
    if user_lang == 'fa':
        system_prompt = "You are a helpful and friendly AI assistant. The user is speaking Persian. You MUST reply in Persian (Farsi)."
    else:
        system_prompt = "You are a helpful and friendly AI assistant. You MUST reply in English."
    
    messages = [{"role": "system", "content": system_prompt}] + user_histories[user_id]
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
        )
        
        ai_reply = response.choices[0].message.content
        user_histories[user_id].append({"role": "assistant", "content": ai_reply})
        
        if len(user_histories[user_id]) > 20:
            user_histories[user_id] = user_histories[user_id][-20:]
        
        return ai_reply
        
    except Exception as e:
        print(f"AI error: {e}")
        if user_lang == 'fa':
            return "متأسفم، الان نمی‌تونم جواب بدم. لطفاً بعداً امتحان کن."
        else:
            return "Sorry, I can't respond right now. Please try again later."

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    try:
        lang = detect(message.text)
    except:
        lang = 'en'
    
    if lang == 'fa':
        welcome_text = "سلام! من یه دستیار هوش مصنوعی هستم. هر سوالی داری بپرس."
    else:
        welcome_text = "Hi! I'm an AI assistant. Ask me anything."
    
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text.strip()
    
    if not user_text:
        return
    
    try:
        lang = detect(user_text)
    except:
        lang = 'en'
    
    bot.send_chat_action(message.chat.id, 'typing')
    ai_reply = get_ai_response(user_id, user_text, lang)
    bot.reply_to(message, ai_reply)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    # حذف هر Webhook موجود
    bot.remove_webhook()
    time.sleep(2)
    
    # اجرای وب‌سرور در پس‌زمینه
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    
    print("bot roshan shod...")
    bot.infinity_polling()