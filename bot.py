import asyncio
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai.client import Mistral   # ← этот импорт обязателен для v2

TOKEN = os.getenv("TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or "1cHOyLt10uR3dQ2HhRPF4JYqZte5cgnd"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = Mistral(api_key=MISTRAL_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Расскажи сон, я его растолкую ✨")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    logger.info(f"Получено: {text[:100]}...")

    await update.message.chat.send_action("typing")

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": "Ты — хороший толкователь снов. Отвечай интересно и по делу."},
                {"role": "user", "content": text}
            ],
            max_tokens=700,
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
        logger.info("Ответ отправлен")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("😔 Mistral временно не отвечает. Попробуй позже.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())