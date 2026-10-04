import telebot
import os
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "سلام! من یه ربات ساده هستم.\nبرای دیدن راهنما بنویس /help")

@bot.message_handler(commands=["help"])
def send_help(message):
    text = (
        "راهنمای ربات:\n\n"
        "/start - شروع\n"
        "/help - همین راهنما\n"
        "/time - ساعت الان\n"
        "/date - تاریخ امروز\n"
        "/about - درباره ربات"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=["time"])
def send_time(message):
    now = datetime.now().strftime("%H:%M:%S")
    bot.reply_to(message, f"ساعت الان: {now}")

@bot.message_handler(commands=["date"])
def send_date(message):
    today = datetime.now().strftime("%Y-%m-%d")
    bot.reply_to(message, f"تاریخ امروز: {today}")

@bot.message_handler(commands=["about"])
def send_about(message):
    bot.reply_to(message, "من یه ربات تلگرام ساده هستم که با پایتون ساخته شدم.")

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