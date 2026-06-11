import telebot
import random
import json
import datetime
import os
from telebot import types
from flask import Flask
from threading import Thread

# =====================
# TELEGRAM BOT
# =====================
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

with open("words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

user_data = {}


# =====================
# FLASK (ДЛЯ RENDER ПОРТА)
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"


def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


# =====================
# XP + STREAK
# =====================
def today():
    return datetime.date.today()


def update_streak(user):
    now = today()
    last = user.get("last_day")

    if last is None:
        user["streak"] = 1
    else:
        last_date = datetime.datetime.strptime(last, "%Y-%m-%d").date()
        diff = (now - last_date).days

        if diff == 1:
            user["streak"] += 1
        elif diff > 1:
            user["streak"] = 1

    user["last_day"] = str(now)


def get_level(score):
    if score <= 3:
        return "A1"
    elif score == 4:
        return "A2"
    else:
        return "B1"


# =====================
# TEST START
# =====================
@bot.message_handler(commands=['test'])
def start_test(message):
    chat_id = message.chat.id

    user_data[chat_id] = {
        "score": 0,
        "xp": 0,
        "q_left": 5,
        "current_correct": None,
        "level": "A1",
        "streak": 0,
        "last_day": None
    }

    send_question(chat_id)


# =====================
# QUESTION
# =====================
def send_question(chat_id):

    if chat_id not in user_data:
        return

    if user_data[chat_id]["q_left"] <= 0:
        score = user_data[chat_id]["score"]
        xp = user_data[chat_id]["xp"]
        level = get_level(score)

        update_streak(user_data[chat_id])
        streak = user_data[chat_id]["streak"]

        bot.send_message(
            chat_id,
            f"🏁 Тест завершён!\n\n"
            f"⭐ XP: {xp}\n"
            f"📊 Level: {level}\n"
            f"🔥 Streak: {streak}"
        )

        del user_data[chat_id]
        return

    word = random.choice(list(words.keys()))
    correct = words[word]

    user_data[chat_id]["current_correct"] = correct

    wrong_answers = [w for w in words.values() if w != correct]
    wrong_choices = random.sample(wrong_answers, 3)

    options = wrong_choices + [correct]
    random.shuffle(options)

    markup = types.InlineKeyboardMarkup()
    labels = ["A", "B", "C", "D"]

    for i in range(4):
        markup.add(
            types.InlineKeyboardButton(
                text=f"{labels[i]}) {options[i]}",
                callback_data=f"ans:{options[i]}"
            )
        )

    bot.send_message(
        chat_id,
        f"❓ Word: *{word}*",
        reply_markup=markup,
        parse_mode="Markdown"
    )


# =====================
# ANSWERS
# =====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("ans:"))
def check_answer(call):

    chat_id = call.message.chat.id

    if chat_id not in user_data:
        bot.answer_callback_query(call.id, "Start /test")
        return

    selected = call.data.split("ans:")[1]
    correct = user_data[chat_id]["current_correct"]

    if selected == correct:
        user_data[chat_id]["score"] += 1
        user_data[chat_id]["xp"] += 10
        bot.answer_callback_query(call.id, "✅ +10 XP")
    else:
        bot.answer_callback_query(call.id, "❌ Wrong")

    user_data[chat_id]["q_left"] -= 1
    send_question(chat_id)


# =====================
# START EVERYTHING
# =====================
if __name__ == "__main__":
    Thread(target=run_web).start()
    print("Bot started")
    bot.infinity_polling()
