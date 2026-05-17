from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
import google.generativeai as genai

TOKEN = os.getenv("TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not GEMINI_API_KEY:
    print("❌ Ошибка: TOKEN или GEMINI_API_KEY не найден!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("✅ Бот успешно запущен!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 8:
        await update.message.reply_text("Расскажи сон подробнее, пожалуйста 😊")
        return

    await update.message.reply_text("🔮 Думаю над твоим сном...")

    try:
        response = model.generate_content(
            f"""Ты опытный, добрый и мудрый толкователь снов. 
Отвечай тепло, по-русски, красиво и поддерживающе. 
Избегай негатива и страшных трактовок.

Сон человека: {text}

Расшифруй его:"""
        )
        
        answer = response.text.strip()
        if answer:
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text("Не смог расшифровать этот сон... Расскажи подробнее?")
            
    except Exception as e:
        print(f"Ошибка Gemini: {e}")
        await update.message.reply_text("😔 Сейчас немного перегружено. Попробуй рассказать сон через пару минут.")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Бот работает...")
app.run_polling()