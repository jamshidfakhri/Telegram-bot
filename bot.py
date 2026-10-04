import telebot
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "سلام! من یه ربات ساده هستم. هر چی بنویسی، همون رو جواب می‌دم.")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, f"تو گفتی: {message.text}")

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