import asyncio
import logging
import os
from typing import Dict, List

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai.client import Mistral   # ← обязательно этот импорт

# ========================= НАСТРОЙКИ =========================
TOKEN = os.getenv("TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or "1cHOyLt10uR3dQ2HhRPF4JYqZte5cgnd"

MODEL = "mistral-large-latest"

SYSTEM_PROMPT = """
Ты — опытный толкователь снов. Отвечай интересно, по делу, с лёгким психологическим уклоном.
Максимум 7-8 предложений. Используй эмодзи умеренно.
Если сна мало деталей — задай уточняющие вопросы.
"""

chat_histories: Dict[int, List[dict]] = {}

# ============================================================

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = Mistral(api_key=MISTRAL_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я толкователь снов на Mistral.\nРасскажи свой сон ✨")

async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.message.chat_id

    logger.info(f"→ Сообщение от {chat_id}: {text[:100]}...")

    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    chat_histories[chat_id].append({"role": "user", "content": text})

    await update.message.chat.send_action("typing")

    try:
        resp = client.chat.complete(
            model=MODEL,
            messages=chat_histories[chat_id],
            temperature=0.7,
            max_tokens=800,
        )
        answer = resp.choices[0].message.content

        chat_histories[chat_id].append({"role": "assistant", "content": answer})

        # Ограничиваем историю
        if len(chat_histories[chat_id]) > 14:
            chat_histories[chat_id] = [chat_histories[chat_id][0]] + chat_histories[chat_id][-13:]

        await update.message.reply_text(answer, parse_mode="Markdown")
        logger.info("✓ Ответ отправлен")

    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        await update.message.reply_text("😔 Mistral не отвечает. Попробуй через 30 секунд.")

def main():
    if not TOKEN:
        logger.error("TOKEN не найден!")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))

    logger.info("🚀 Бот запущен на Bothost (GitHub)")
    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())