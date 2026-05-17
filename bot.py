import asyncio
import logging
import os
from typing import Dict, List

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai.client import Mistral   # Новый импорт

# ========================= НАСТРОЙКИ =========================
TOKEN = os.getenv("TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or "1cHOyLt10uR3dQ2HhRPF4JYqZte5cgnd"

MODEL = "mistral-large-latest"

SYSTEM_PROMPT = """
Ты — глубокий, эмпатичный и мудрый толкователь снов...
(твой промпт остаётся тот же)
"""

chat_histories: Dict[int, List[dict]] = {}

# ============================================================

# Улучшенное логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # ← DEBUG вместо INFO
)
logger = logging.getLogger(__name__)

client = Mistral(api_key=MISTRAL_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Команда /start от {update.message.chat_id}")
    await update.message.reply_text(
        "👋 Привет! Я — толкователь снов на Mistral AI.\n\n"
        "Расскажи свой сон как можно подробнее ✨"
    )


async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    chat_id = update.message.chat_id
    logger.info(f"Получено сообщение от {chat_id}: {user_text[:100]}...")

    try:
        if chat_id not in chat_histories:
            chat_histories[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

        chat_histories[chat_id].append({"role": "user", "content": user_text})

        await update.message.chat.send_action("typing")

        response = client.chat.complete(
            model=MODEL,
            messages=chat_histories[chat_id],
            temperature=0.75,
            max_tokens=900,
        )

        answer = response.choices[0].message.content
        logger.info(f"Ответ Mistral получен ({len(answer)} символов)")

        chat_histories[chat_id].append({"role": "assistant", "content": answer})

        if len(chat_histories[chat_id]) > 15:
            chat_histories[chat_id] = [chat_histories[chat_id][0]] + chat_histories[chat_id][-14:]

        await update.message.reply_text(answer, parse_mode="Markdown")
        logger.info(f"Ответ отправлен пользователю {chat_id}")

    except Exception as e:
        logger.error(f"ОШИБКА при обработке сообщения {chat_id}: {e}", exc_info=True)
        await update.message.reply_text("😔 Произошла ошибка. Попробуй ещё раз через минуту.")


def main():
    if not TOKEN:
        logger.error("TOKEN не найден в переменных окружения!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))

    logger.info("🚀 Бот запущен успешно! Ожидаем сообщений...")
    app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())