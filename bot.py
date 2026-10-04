import telebot
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "salam! man ye robotam.\nسلام! من یه رباتم.\n\nharfi dari? benevis ta javab bedam\nحرفی داری؟ بنویس تا جواب بدم")

@bot.message_handler(func=lambda message: True)
def reply(message):
    text = message.text.lower().strip()
    
    if text in ["salam", "سلام", "hi", "hello"]:
        bot.send_message(message.chat.id, "salam! chetori?\nسلام! چطوری؟")
    
    elif text in ["khubi?", "khubi", "خوبی؟", "خوبی", "chetori?", "chetori", "چطوری؟", "چطوری"]:
        bot.send_message(message.chat.id, "man khubam, to chetori?\nمن خوبم، تو چطوری؟")
    
    elif text in ["esmet chiye?", "esmet chiye", "اسمت چیه؟", "اسمت چیه", "what is your name?", "what is your name"]:
        bot.send_message(message.chat.id, "esmam robot hast\nاسمم ربات هست")
    
    elif text in ["khodahafez", "خداحافظ", "bye", "goodbye"]:
        bot.send_message(message.chat.id, "khodahafez! movazebe khodet bash\nخداحافظ! مواظب خودت باش")
    
    else:
        bot.send_message(message.chat.id, "nemifahmam chi migi. lotfan farsi ya engilisi benevis\nنمی‌فهمم چی می‌گی. لطفاً فارسی یا انگلیسی بنویس")

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
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    print("bot roshan shod...")
    bot.polling()