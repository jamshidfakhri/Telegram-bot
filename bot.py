import telebot
import os
import threading
import time
import sqlite3
import urllib.request
import urllib.parse
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
SITE_URL = os.environ.get("SITE_URL", "https://myfirstweb-4sde.onrender.com")

bot = telebot.TeleBot(TOKEN)
bot.set_chat_menu_button(menu_button=types.MenuButtonCommands())

user_replies = {}  # ذخیره‌ی آخرین conversation_id برای هر ادمین

def send_reply_to_site(conversation_id, text):
    url = f"{SITE_URL}/api/admin_reply"
    data = json.dumps({
        "conversation_id": conversation_id,
        "text": text
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "سلام! من ربات سایتم.")

# وقتی ادمین روی پیام سایت Reply می‌زنه
@bot.message_handler(func=lambda message: str(message.from_user.id) == str(ADMIN_ID) and message.reply_to_message is not None)
def admin_reply_handler(message):
    reply_to = message.reply_to_message
    
    if not reply_to.text or "شناسه گفتگو:" not in reply_to.text:
        return
    
    # استخراج conversation_id
    try:
        lines = reply_to.text.split("\n")
        conv_line = [l for l in lines if "شناسه گفتگو:" in l][0]
        conversation_id = conv_line.replace("شناسه گفتگو:", "").strip()
    except Exception as e:
        print(f"Extract error: {e}")
        return
    
    # ارسال پاسخ به سایت
    if send_reply_to_site(conversation_id, message.text):
        bot.reply_to(message, "پاسخ به سایت ارسال شد ✅")
    else:
        bot.reply_to(message, "خطا در ارسال به سایت ❌")

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
    bot.remove_webhook()
    time.sleep(2)
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    print("bot roshan shod...")
    bot.infinity_polling()