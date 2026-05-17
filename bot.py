import asyncio
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai import Mistral   # Старый импорт для Bothost

# ========================= НАСТРОЙКИ =========================
TOKEN = os.getenv("TOKEN")
MISTRAL_API_KEY = "1cHOyLt10uR3dQ2HhRPF4JYqZte5cgnd"   # ← зашит напрямую

MODEL = "mistral-large-latest"

SYSTEM_PROMPT = """
Ты — мудрый и эмпатичный толкователь снов.
Отвечай интересно, с душой, но не очень длинно (6-8 предложений).
Используй эмодзи умеренно.
Если деталей мало — задай 1-2 уточняющих вопроса.
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Mistral(api_key=MISTRAL_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я — толкователь снов на Mistral AI.\n\n"
        "Расскажи свой сон как можно подробнее ✨"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    logger.info(f"Получено сообщение от {update.message.chat_id}")

    await update.message.chat.send_action("typing")

    try:
        response = client.chat.complete(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.75,
            max_tokens=800,
        )
        
        answer = response.choices[0].message.content
        await update.message.reply_text(answer, parse_mode="Markdown")
        logger.info("Ответ успешно отправлен")

    except Exception as e:
        logger.error(f"Ошибка Mistral: {e}")
        await update.message.reply_text("😔 Mistral сейчас не отвечает.\nПопробуй отправить сон через 20-30 секунд.")


def main():
    if not TOKEN:
        logger.error("TOKEN не найден!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Бот запущен — ждём сны...")
    app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())