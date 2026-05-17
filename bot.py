from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
import random

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ TOKEN не найден!")
    exit(1)

print("✅ Бот 'Мир Сновидений' запущен!")

# База знаний для толкования снов
DREAM_TEMPLATES = {
    "летать": ["Ты летал? Это отличный знак свободы и уверенности в себе! Твоя душа хочет большего.", 
               "Полёт во сне — символ того, что ты растешь и преодолеваешь ограничения."],
    "падать": ["Падение часто означает страх потери контроля. Возможно, в жизни есть ситуация, которую ты боишься отпустить."],
    "преследовать": ["Тебя кто-то преследовал? Это может быть нерешённая проблема или страх, от которого ты убегаешь."],
    "вода": ["Вода — символ эмоций. Чистая = спокойствие, мутная = внутренние переживания."],
    "зубы": ["Выпадение зубов часто связано со страхом потери внешнего вида, уверенности или контроля."],
    "умер": ["Смерть во сне — почти всегда символ трансформации и нового этапа в жизни."],
    "школа": ["Школа или экзамен — подсознание проверяет, готов ли ты к новым вызовам."],
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    if len(text) < 8:
        await update.message.reply_text("Расскажи сон подробнее, пожалуйста 😊")
        return

    await update.message.reply_text("🔮 Думаю над твоим сном...")

    # Ищем ключевые слова
    response = None
    for keyword, answers in DREAM_TEMPLATES.items():
        if keyword in text:
            response = random.choice(answers)
            break

    # Если ничего не нашли — общий ответ
    if not response:
        responses = [
            "Интересный сон... Он говорит о твоём внутреннем желании изменений и свободы.",
            "Твой сон символизирует переход на новый этап жизни. Что ты чувствовал во сне?",
            "Подсознание подсказывает тебе обратить внимание на свои эмоции и желания.",
            "Этот сон — знак, что ты готов к чему-то большему. Что ты думаешь об этом?",
            "Красивый сон. В нём много символов роста и саморазвития."
        ]
        response = random.choice(responses)

    await update.message.reply_text(response)


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Бот работает...")
app.run_polling()