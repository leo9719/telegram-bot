from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
import random

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ TOKEN не найден!")
    exit(1)

print("✅ Бот 'Мир Сновидений' запущен!")

def interpret_dream(dream_text: str) -> str:
    text = dream_text.lower()
    
    intro = "🔮 Я внимательно проанализировал твой сон. Вот что он может значить:"

    interpretations = []

    # Основные символы
    if any(w in text for w in ["летал", "летать", "полет", "летаю", "летишь"]):
        interpretations.append("**Полёт** — один из самых мощных архетипов. По Юнгу это символ духовного подъёма и стремления к самореализации. Твоя душа сейчас просит свободы и расширения горизонтов. Ты готов подняться над текущими ограничениями.")
    
    if any(w in text for w in ["падал", "падать", "упал", "сорвался"]):
        interpretations.append("**Падение** часто отражает страх потери контроля. Фрейд видел в этом тревогу по поводу жизненной нестабильности. Возможно, в реальной жизни есть ситуация, где ты боишься «упасть» — потерять статус, отношения или уверенность.")
    
    if any(w in text for w in ["преслед", "гонял", "убегал", "погоня"]):
        interpretations.append("**Преследование** — классический символ нерешённого внутреннего конфликта. То, от чего ты убегаешь во сне, часто является частью тебя самого (страх, вина, подавленная эмоция), которую пора принять.")
    
    if any(w in text for w in ["вода", "море", "река", "океан", "тонуть"]):
        interpretations.append("**Вода** символизирует эмоциональное состояние. Чистая и спокойная — гармония. Бурная или тёмная — сильные, возможно, подавленные чувства. Если ты тонул — это сигнал, что эмоции сейчас переполняют и требуют внимания.")
    
    if any(w in text for w in ["зуб", "зубы", "выпал"]):
        interpretations.append("**Зубы** — древний символ уверенности в себе и личной силы. Выпадение часто связано со страхом старения, потери привлекательности или неспособности «укусить» жизнь.")
    
    if any(w in text for w in ["умер", "смерть", "погиб", "хоронил"]):
        interpretations.append("**Смерть** во сне почти никогда не бывает буквальной. Это мощный символ трансформации. Старое «я» умирает, чтобы дать место новому этапу жизни. Юнг называл такие сны «инициацией».")

    # Если ничего конкретного не нашлось
    if not interpretations:
        interpretations = [
            "Этот сон несёт важное послание от твоего подсознания. Он отражает внутренние процессы роста и переход на новый уровень.",
            "Твоя психика сейчас активно перерабатывает переживания. Сон показывает, что ты стоишь перед важным выбором или трансформацией.",
            "В этом сне много архетипической энергии. Он говорит о твоём желании стать более цельным и свободным.",
        ]

    main = random.choice(interpretations)
    
    ending = "\n\n💡 Что ты чувствовал во сне? Страх, радость, спокойствие? Эти эмоции — ключ к более точной расшифровке."

    return f"{intro}\n\n{main}{ending}"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 10:
        await update.message.reply_text("Расскажи сон подробнее, пожалуйста 😊")
        return

    await update.message.reply_text("🔮 Погружаюсь в твой сон... Это может занять пару секунд.")

    interpretation = interpret_dream(text)
    await update.message.reply_text(interpretation)


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Бот работает...")
app.run_polling()