from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
import random

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ TOKEN не найден!")
    exit(1)

print("✅ Бот 'Мир Сновидений' успешно запущен!")

# Простая база толкований
DREAM_RESPONSES = [
    "Твой сон символизирует стремление к свободе и новым высотам. Ты готов к изменениям.",
    "Это очень позитивный сон. Он говорит о твоём внутреннем росте и желании большего.",
    "Подсознание показывает, что ты преодолеваешь какие-то ограничения в жизни.",
    "Сон говорит о том, что ты ищешь свободу и хочешь почувствовать себя легче.",
    "Интересный сон! Он отражает твои амбиции и веру в свои силы.",
    "Ты летал? Это почти всегда хороший знак — ты растешь над собой.",
    "Такой сон часто приходит перед важными изменениями в жизни."
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 10:
        await update.message.reply_text("Расскажи сон подробнее, пожалуйста 😊")
        return

    await update.message.reply_text("🔮 Думаю над твоим сном...")

    # Случайный ответ
    response = random.choice(DREAM_RESPONSES)
    
    # Иногда добавляем вопрос для продолжения диалога
    if random.random() > 0.7:
        response += "\n\nА что ты чувствовал во сне?"

    await update.message.reply_text(response)


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Бот работает...")
app.run_polling()