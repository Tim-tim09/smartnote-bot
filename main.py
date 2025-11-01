import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import openai
from openai import OpenAI

# Загружаем токены
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Настраиваем клиент для OpenRouter
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        "👋 Привет, <b>{name}</b>!\n\n"
        "Я — <b>SmartNotes AI</b> 🤖\n"
        "Твой личный ассистент, который превращает тексты, голосовые и документы "
        "в краткие и понятные <b>конспекты</b> ✍️\n\n"
        "📘 <b>Что я умею:</b>\n"
        "• /summarize — сделать конспект по тексту 🧩\n"
        "• Отправь голосовое — я расшифрую и сделаю конспект 🎧\n\n"
        "🚀 Готов начать? Просто напиши или пришли аудио!"
    ).format(name=message.from_user.first_name)

    await message.answer(welcome_text, parse_mode="HTML")


# Функция для разбиения длинных сообщений
def split_text(text, max_length=4000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Команда /summarize
@dp.message(Command("summarize"))
async def summarize(message: types.Message):
    text = message.text.replace("/summarize", "").strip()

    if not text:
        await message.answer("⚠️ После команды добавь текст, например:\n/summarize Сегодня я изучал машинное обучение и статистику.")
        return

    await message.answer("✍️ Создаю конспект, подожди немного...")

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # можешь поменять, например: 'mistralai/mixtral-8x7b'
            messages=[
                {"role": "system", "content": "Ты умный ассистент, который делает краткие и понятные конспекты."},
                {"role": "user", "content": f"Создай краткий конспект из следующего текста:\n{text}"}
            ],
        )

        summary = completion.choices[0].message.content.strip()

        for part in split_text(summary):
            await message.answer(part)

    except Exception as e:
        await message.answer(f"❌ Ошибка при обращении к API: {e}")

async def main():
    print("✅ Бот запущен через OpenRouter!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
