import asyncio
import random
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
)

import os

TOKEN = os.getenv("TOKEN")

words = [
    ("apple", "яблоко"),
    ("house", "дом"),
    ("book", "книга"),
    ("water", "вода"),
    ("friend", "друг"),
    ("computer", "компьютер"),
    ("school", "школа"),
    ("money", "деньги"),
    ("family", "семья"),
    ("language", "язык"),
]

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
