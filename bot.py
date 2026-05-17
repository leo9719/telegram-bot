from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
import google.generativeai as genai

TOKEN = os.getenv("TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not GEMINI_API_KEY:
    print("❌ Ошибка: Нет TOKEN или GEMINI_API_KEY")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("✅ Бот запущен!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 10:
        await update.message.reply_text("Расскажи сон подробнее, пожалуйста 😊")
        return

    await update.message.reply_text("🔮 Анализирую твой сон...")

    try:
        prompt = f"""Ты добрый и мудрый толкователь снов. 
Отвечай тепло, по-русски, позитивно и понятно. 
Не используй страшные трактовки.

Сон: {text}

Толкование:"""

        response = model.generate_content(prompt, 
                                         generation_config={"temperature": 0.7})
        
        answer = response.text.strip()
        if answer:
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text("Не получилось расшифровать... Расскажи сон подробнее?")
            
    except Exception as e:
        print(f"❌ Ошибка Gemini: {e}")
        await update.message.reply_text("😔 Сейчас Gemini немного перегружен. Попробуй через 10–20 секунд.")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Бот работает...")
app.run_polling()