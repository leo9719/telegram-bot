from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
import google.generativeai as genai

# ================= НАСТРОЙКИ =================
TOKEN = os.getenv("TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")   # ← добавим позже

if not TOKEN or not GEMINI_API_KEY:
    print("❌ Ошибка: Не найдены TOKEN или GEMINI_API_KEY")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("✅ Бот толкователь снов запущен!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 8:
        await update.message.reply_text("Расскажи сон подробнее, пожалуйста 😊")
        return

    await update.message.reply_text("🔮 Думаю над твоим сном...")

    try:
        response = model.generate_content(
            f"""Ты очень добрый, мудрый и теплый толкователь снов. 
Отвечай по-русски, красиво, поддерживающе и понятно. 
Не используй страшные и негативные трактовки.

Сон: {text}"""
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("😔 Что-то пошло не так... Попробуй чуть позже.")

# ================= ЗАПУСК =================
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Бот работает...")
app.run_polling()