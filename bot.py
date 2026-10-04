import telebot
import os
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# فعال کردن دکمه‌ی Menu (پایین سمت چپ)
bot.set_chat_menu_button(menu_button=types.MenuButtonCommands())

# ساخت کیبورد پایین صفحه
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_help = types.KeyboardButton("راهنما")
    btn_time = types.KeyboardButton("ساعت")
    btn_date = types.KeyboardButton("تاریخ")
    btn_about = types.KeyboardButton("درباره ربات")
    keyboard.add(btn_help, btn_time)
    keyboard.add(btn_date, btn_about)
    return keyboard

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "سلام! من یه ربات ساده هستم.\nاز دکمه‌های پایین استفاده کن:",
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=["help"])
def send_help(message):
    text = (
        "راهنمای ربات:\n\n"
        "راهنما - همین راهنما\n"
        "ساعت - ساعت الان\n"
        "تاریخ - تاریخ امروز\n"
        "درباره ربات - درباره ربات"
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

# دکمه‌های کیبورد
@bot.message_handler(func=lambda message: message.text == "راهنما")
def btn_help(message):
    send_help(message)

@bot.message_handler(func=lambda message: message.text == "ساعت")
def btn_time(message):
    send_time(message)

@bot.message_handler(func=lambda message: message.text == "تاریخ")
def btn_date(message):
    send_date(message)

@bot.message_handler(func=lambda message: message.text == "درباره ربات")
def btn_about(message):
    send_about(message)

# پیام‌های معمولی
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