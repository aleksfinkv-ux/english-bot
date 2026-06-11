import telebot
import random
import json
from telebot import types

bot = telebot.TeleBot("8968911517:AAE736Z9Go3JwrhfpQFt8g8Iy-iC8BMfVZA")

# 1. загрузка слов
with open("words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

# 2. данные пользователей (тесты)
user_data = {}

@bot.message_handler(commands=['test'])
def start_test(message):
    chat_id = message.chat.id

    user_data[chat_id] = {
        "score": 0,
        "q_left": 5,
        "current_correct": None
    }

    send_question(chat_id)

def send_question(chat_id):

    # если тест закончился
    if user_data[chat_id]["q_left"] <= 0:
        score = user_data[chat_id]["score"]

        bot.send_message(
            chat_id,
            f"🏁 Тест завершён!\n\n"
            f"✅ Результат: {score}/5"
        )

        del user_data[chat_id]
        return

    # слово
    word = random.choice(list(words.keys()))
    correct = words[word]

    user_data[chat_id]["current_correct"] = correct

    # неправильные варианты
    wrong_answers = list(words.values())
    wrong_answers.remove(correct)
    wrong_choices = random.sample(wrong_answers, 3)

    options = wrong_choices + [correct]
    random.shuffle(options)

    markup = types.InlineKeyboardMarkup()

    labels = ["A", "B", "C", "D"]

    for i in range(4):
        markup.add(
            types.InlineKeyboardButton(
                text=f"{labels[i]}) {options[i]}",
                callback_data=f"answer:{options[i]}"
            )
        )

    bot.send_message(
        chat_id,
        f"❓ Переведи слово: *{word}*",
        reply_markup=markup,
        parse_mode="Markdown"
    )
@bot.callback_query_handler(func=lambda call: call.data.startswith("answer:"))
def check_answer(call):

    chat_id = call.message.chat.id
    selected = call.data.split("answer:")[1]

    correct = user_data[chat_id]["current_correct"]

    if selected == correct:
        user_data[chat_id]["score"] += 1
        bot.answer_callback_query(call.id, "✅ Правильно!")
        bot.send_message(chat_id, "👍 Верно!")
    else:
        bot.answer_callback_query(call.id, "❌ Неправильно")
        bot.send_message(chat_id, f"❌ Неверно!\nПравильный ответ: {correct}")

    user_data[chat_id]["q_left"] -= 1

    send_question(chat_id)
    
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Привет! 👋\n"
        "Я помогу учить английские слова.\n\n"
        "/word - получить новое слово\n"
        "/quiz - пройти тест"
    )

async def word(update: Update, context: CallbackContext):
    english, russian = random.choice(words)

    context.user_data["answer"] = russian

    await update.message.reply_text(
        f"📚 Слово:\n\n{english}\n\n"
        f"Перевод:\n{russian}"
    )

async def quiz(update: Update, context: CallbackContext):
    english, russian = random.choice(words)

    context.user_data["quiz_answer"] = russian

    await update.message.reply_text(
        f"❓ Как переводится слово:\n\n{english}"
    )

async def handle_message(update: Update, context: CallbackContext):
    if "quiz_answer" not in context.user_data:
        return

    answer = context.user_data["quiz_answer"].lower()
    user_answer = update.message.text.lower()

    if answer == user_answer:
        await update.message.reply_text("✅ Правильно!")
    else:
        await update.message.reply_text(
            f"❌ Неверно.\nПравильный ответ: {answer}"
        )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "/word - новое слово\n"
        "/quiz - тест"
    )

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("word", word))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("help", help_command))

    from telegram.ext import MessageHandler, filters

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Бот запущен...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
    
bot.infinity_polling()
