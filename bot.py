import asyncio
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai import Mistral

# ========================= НАСТРОЙКИ =========================
TOKEN = os.getenv("TOKEN")
MISTRAL_API_KEY = "1cHOyLt10uR3dQ2HhRPF4JYqZte5cgnd"

SYSTEM_PROMPT = """
Ты — мудрый и empathetic толкователь снов. 
Отвечай интересно, глубоко, но не слишком длинно (6-8 предложений).
Используй эмодзи умеренно.
"""

# Хранилище: {chat_id: {"mode": "waiting" или "dream_mode", "history": [...]}}
user_data = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Mistral(api_key=MISTRAL_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_data[chat_id] = {"mode": "waiting", "history": []}

    await update.message.reply_text(
        "👋 Привет! Я толкователь снов.\n\n"
        "Расскажи свой сон — я помогу его разобрать ✨\n"
        "После первого ответа можешь задавать любые уточняющие вопросы."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {"mode": "waiting", "history": []}

    await update.message.chat.send_action("typing")

    try:
        if user_data[chat_id]["mode"] == "waiting":
            # Первый сон
            user_data[chat_id]["history"] = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Расскажи сон: {text}"}
            ]

            response = client.chat.complete(
                model="mistral-large-latest",
                messages=user_data[chat_id]["history"],
                temperature=0.75,
                max_tokens=800,
            )
            answer = response.choices[0].message.content

            user_data[chat_id]["history"].append({"role": "assistant", "content": answer})
            user_data[chat_id]["mode"] = "dream_mode"

            await update.message.reply_text(
                answer + "\n\n"
                "Теперь можешь задавать мне любые вопросы по этому сну.\n"
                "Чтобы начать новый сон — напиши /new"
            )

        else:
            # Режим разбора сна (дополнительные вопросы)
            user_data[chat_id]["history"].append({"role": "user", "content": text})

            response = client.chat.complete(
                model="mistral-large-latest",
                messages=user_data[chat_id]["history"],
                temperature=0.75,
                max_tokens=800,
            )
            answer = response.choices[0].message.content

            user_data[chat_id]["history"].append({"role": "assistant", "content": answer})

            await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("😔 Что-то пошло не так. Попробуй ещё раз.")


async def new_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_data[chat_id] = {"mode": "waiting", "history": []}
    await update.message.reply_text(
        "🆕 Режим нового сна активирован!\n\nРасскажи свой следующий сон ✨"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_dream))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Бот-толкователь снов запущен")
    app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())