import telebot
import os
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# فعال کردن دکمه‌ی Menu
bot.set_chat_menu_button(menu_button=types.MenuButtonCommands())

# دیکشنری برای ذخیره اسم کاربرا
user_names = {}

# ساخت کیبورد
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_help = types.KeyboardButton("راهنما")
    btn_time = types.KeyboardButton("ساعت")
    btn_date = types.KeyboardButton("تاریخ")
    btn_about = types.KeyboardButton("درباره ربات")
    btn_setname = types.KeyboardButton("ثبت اسم")
    keyboard.add(btn_help, btn_time)
    keyboard.add(btn_date, btn_about)
    keyboard.add(btn_setname)
    return keyboard

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    
    if user_id in user_names:
        name = user_names[user_id]
        text = f"سلام {name}! خوش برگشتی."
    else:
        text = "سلام! من یه ربات ساده هستم.\nاول اسمت رو ثبت کن."
    
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())

@bot.message_handler(commands=["setname"])
def ask_name(message):
    bot.reply_to(message, "اسمت چیه؟")
    bot.register_next_step_handler(message, save_name)

def save_name(message):
    user_id = message.from_user.id
    name = message.text.strip()
    
    if name == "":
        bot.reply_to(message, "اسم نمی‌تونه خالی باشه. دوباره امتحان کن.")
        return
    
    user_names[user_id] = name
    bot.reply_to(message, f"باشه {name}، اسمت رو ذخیره کردم.")

@bot.message_handler(commands=["help"])
def send_help(message):
    text = (
        "راهنمای ربات:\n\n"
        "راهنما - همین راهنما\n"
        "ساعت - ساعت الان\n"
        "تاریخ - تاریخ امروز\n"
        "درباره ربات - درباره ربات\n"
        "ثبت اسم - ثبت اسم خودت"
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

@bot.message_handler(func=lambda message: message.text == "ثبت اسم")
def btn_setname(message):
    ask_name(message)

# پیام‌های معمولی
@bot.message_handler(func=lambda message: True)
def echo(message):
    user_id = message.from_user.id
    
    if user_id in user_names:
        name = user_names[user_id]
        bot.reply_to(message, f"{name} جان، تو گفتی: {message.text}")
    else:
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