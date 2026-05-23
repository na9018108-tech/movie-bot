import telebot
import os
from flask import Flask
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
movie_db = {}

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    parts = message.text.split()
    if len(parts) == 1:
        bot.reply_to(message, "🎬 *Movie Bot mein Swagat hai!*\n\nMovie link use karo dekhne ke liye.", parse_mode='Markdown')
        return
    movie_id = parts[1]
    if movie_id in movie_db:
        movie = movie_db[movie_id]
        bot.reply_to(message, f"⏳ *{movie['name']}* load ho rahi hai...", parse_mode='Markdown')
        bot.send_video(message.chat.id, movie['file_id'], caption=f"🎬 {movie['name']}")
    else:
        bot.reply_to(message, "❌ Movie nahi mili! Link check karo.")

@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "❌ Sirf admin upload kar sakta hai!")
        return
    forwarded = bot.forward_message(CHANNEL_ID, message.chat.id, message.message_id)
    if message.video:
        file_id = message.video.file_id
    else:
        file_id = message.document.file_id
    movie_id = str(forwarded.message_id)
    movie_db[movie_id] = {'file_id': file_id, 'name': message.caption or "Movie"}
    link = f"https://t.me/{bot.get_me().username}?start={movie_id}"
    bot.reply_to(message, f"✅ Upload ho gaya!\n\n🎬 Movie: {message.caption or 'Movie'}\n🔗 Link: {link}\n\nYeh link share karo!")

@bot.message_handler(commands=['list'])
def list_movies(message):
    if not movie_db:
        bot.reply_to(message, "📭 Koi movie nahi hai abhi.")
        return
    text = "🎬 *Movies List:*\n\n"
    for mid, movie in movie_db.items():
        link = f"https://t.me/{bot.get_me().username}?start={mid}"
        text += f"• [{movie['name']}]({link})\n"
    bot.reply_to(message, text, parse_mode='Markdown')

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    print("Bot start ho raha hai...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    bot.infinity_polling()
