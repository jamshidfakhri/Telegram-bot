import telebot
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "salam! man ye robotam. harfi dari? benevis ta javab bedam")

@bot.message_handler(func=lambda message: True)
def reply(message):
    text = message.text.lower()
    
    if text == "salam":
        bot.send_message(message.chat.id, "salam! chetori?")
    elif text == "khubi?":
        bot.send_message(message.chat.id, "man ke khubam, to chetori?")
    elif text == "esmet chiye?":
        bot.send_message(message.chat.id, "esmam robot hast")
    elif text == "khodahafez":
        bot.send_message(message.chat.id, "khodahafez! movazebe khodet bash")
    else:
        bot.send_message(message.chat.id, "nemifahmam chi migi. farsi benevis lotfan")

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