import telebot
import os
import threading
import time
import sqlite3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")

bot = telebot.TeleBot(TOKEN)

bot.set_chat_menu_button(menu_button=types.MenuButtonCommands())

# ---------------- دیتابیس ----------------
DB_NAME = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user_name(user_id, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, name) VALUES (?, ?)",
        (user_id, name)
    )
    conn.commit()
    conn.close()

def get_user_name(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    result = cursor.fetchall()
    conn.close()
    return [row[0] for row in result]

def is_admin(user_id):
    if not ADMIN_ID:
        return False
    return str(user_id) == str(ADMIN_ID)

# ---------------- کیبورد ----------------
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_help = types.KeyboardButton("راهنما")
    btn_time = types.KeyboardButton("ساعت")
    btn_date = types.KeyboardButton("تاریخ")
    btn_about = types.KeyboardButton("درباره ربات")
    btn_setname = types.KeyboardButton("ثبت اسم")
    btn_inline = types.KeyboardButton("منوی شیشه‌ای")
    btn_photo = types.KeyboardButton("عکس")
    btn_file = types.KeyboardButton("فایل")
    keyboard.add(btn_help, btn_time)
    keyboard.add(btn_date, btn_about)
    keyboard.add(btn_setname, btn_inline)
    keyboard.add(btn_photo, btn_file)
    return keyboard

def inline_menu():
    markup = types.InlineKeyboardMarkup()
    btn_time = types.InlineKeyboardButton("ساعت", callback_data="show_time")
    btn_date = types.InlineKeyboardButton("تاریخ", callback_data="show_date")
    btn_about = types.InlineKeyboardButton("درباره ربات", callback_data="show_about")
    markup.add(btn_time, btn_date)
    markup.add(btn_about)
    return markup

# ---------------- دستورها ----------------
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    
    if name:
        text = f"سلام {name}! خوش برگشتی."
    else:
        text = "سلام! من یه ربات ساده هستم.\nاول اسمت رو ثبت کن."
    
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())

@bot.message_handler(commands=["menu"])
def send_inline_menu(message):
    bot.reply_to(message, "چه کاری می‌خوای بکنم؟", reply_markup=inline_menu())

@bot.message_handler(commands=["setname"])
def ask_name(message):
    bot.reply_to(message, "اسمت چیه؟")
    bot.register_next_step_handler(message, save_name)

def save_name(message):
    user_id = message.from_user.id
    name = message.text.strip()
    
    if name == "":
        bot.reply_to(message, "اسم نمی‌تونه خالی باشه.")
        return
    
    save_user_name(user_id, name)
    bot.reply_to(message, f"باشه {name}، اسمت رو ذخیره کردم.")

@bot.message_handler(commands=["help"])
def send_help(message):
    text = (
        "راهنمای ربات:\n\n"
        "راهنما - همین راهنما\n"
        "ساعت - ساعت الان\n"
        "تاریخ - تاریخ امروز\n"
        "درباره ربات - درباره ربات\n"
        "ثبت اسم - ثبت اسم خودت\n"
        "منوی شیشه‌ای - نمایش دکمه‌های شیشه‌ای\n"
        "عکس - ارسال یه عکس نمونه\n"
        "فایل - ارسال یه فایل نمونه"
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

@bot.message_handler(commands=["photo"])
def send_photo(message):
    photo_url = "https://picsum.photos/600/400"
    bot.send_photo(message.chat.id, photo_url, caption="این یه عکس نمونه‌ست.")

@bot.message_handler(commands=["file"])
def send_file(message):
    file_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    bot.send_document(message.chat.id, file_url, caption="این یه فایل PDF نمونه‌ست.")

# ---------------- دستورهای ادمین ----------------
@bot.message_handler(commands=["stats"])
def send_stats(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "اجازه نداری.")
        return
    
    users = get_all_users()
    bot.reply_to(message, f"تعداد کاربران: {len(users)}")

@bot.message_handler(commands=["broadcast"])
def ask_broadcast(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "اجازه نداری.")
        return
    
    bot.reply_to(message, "پیام همگانی رو بنویس:")
    bot.register_next_step_handler(message, send_broadcast)

def send_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    
    text = message.text.strip()
    if not text:
        bot.reply_to(message, "پیام نمی‌تونه خالی باشه.")
        return
    
    users = get_all_users()
    count = 0
    
    for user_id in users:
        try:
            bot.send_message(user_id, text)
            count += 1
            time.sleep(0.05)
        except Exception:
            pass
    
    bot.reply_to(message, f"پیام به {count} کاربر ارسال شد.")

# ---------------- دکمه‌های کیبورد ----------------
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

@bot.message_handler(func=lambda message: message.text == "منوی شیشه‌ای")
def btn_inline(message):
    send_inline_menu(message)

@bot.message_handler(func=lambda message: message.text == "عکس")
def btn_photo(message):
    send_photo(message)

@bot.message_handler(func=lambda message: message.text == "فایل")
def btn_file(message):
    send_file(message)

# ---------------- دکمه‌های شیشه‌ای ----------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "show_time":
        now = datetime.now().strftime("%H:%M:%S")
        bot.answer_callback_query(call.id, f"ساعت الان: {now}")
    elif call.data == "show_date":
        today = datetime.now().strftime("%Y-%m-%d")
        bot.answer_callback_query(call.id, f"تاریخ امروز: {today}")
    elif call.data == "show_about":
        bot.answer_callback_query(call.id, "من یه ربات ساده پایتونیم!")

# ---------------- پیام‌های معمولی ----------------
@bot.message_handler(func=lambda message: True)
def echo(message):
    user_id = message.from_user.id
    name = get_user_name(user_id)
    
    if name:
        bot.reply_to(message, f"{name} جان، تو گفتی: {message.text}")
    else:
        bot.reply_to(message, f"تو گفتی: {message.text}")

# ---------------- وب‌سرور ----------------
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
    init_db()
    bot.remove_webhook()
    time.sleep(2)
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    print("bot roshan shod...")
    bot.infinity_polling()