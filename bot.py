import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from google import genai
from google.genai import types as genai_types
import edge_tts

# =====================================================================
# Загрузка токенов из переменных окружения (.env)
def _load_dotenv(path=".env"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# =====================================================================

# Проверка на случай, если забыли вставить токен
if not BOT_TOKEN or BOT_TOKEN == "ТВОЙ_TELEGRAM_BOT_TOKEN":
    raise ValueError("ОШИБКА: Укажите корректный BOT_TOKEN в файле bot.py!")

if not GEMINI_API_KEY or GEMINI_API_KEY == "ТВОЙ_GEMINI_API_KEY":
    raise ValueError("ОШИБКА: Укажите корректный GEMINI_API_KEY в файле bot.py!")

# Инициализация бота и клиента Gemini
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

# Промпт с встроенной логикой SOS-Детектора
SYSTEM_PROMPT = """
Ты — заботливый помощник для людей, которым трудно читать мелкий текст на упаковках лекарств, квитанциях или инструкциях.

Сначала проверишь фото на наличие КРИТИЧЕСКИХ ОПАСНОСТЕЙ (просроченный срок годности, фатальные противопоказания, ядовитые вещества, категории "строго по рецепту" или "опасно при беременности/детям").

Сформируй ответ строго по следующей структуре:

1. 🚨 **SOS ПРЕДУПРЕЖДЕНИЕ:** (Заполняй ЭТОТ ПУНКТ ТОЛЬКО если есть прямая угроза здоровью или критическое ограничение. Напиши это крупно и сразу. Если опасностей нет — пропусти этот пункт полностью!)
2. 📦 **Что это такое:** (1 простое предложение понятным языком)
3. 📋 **Как использовать / принимать:** (пошагово, кратко и четко)
4. ⚠️ **Важно помнить:** (обычные предостережения, условия хранения)

Пиши коротко, без сложных медицинских терминов и лишней "воды".
"""

@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "Привет! Я помощник «Ясный Текст».\n\n"
        "📸 **Отправь мне фото** упаковки лекарства, инструкции или квитанции.\n"
        "Я найду самое главное, проверю на опасности (SOS-детектор), перепишу простыми словами и озвучу голосом!"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(F.photo)
async def handle_photo(message: Message):
    status_msg = await message.answer("🔍 *Анализирую текст и проверяю на SOS-предупреждения...*", parse_mode="Markdown")
    
    # 1. Скачиваем фото
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file_info.file_path)
    image_data = file_bytes.read()

    try:
        # 2. Обработка через Gemini 2.5 Flash
        response = ai_client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[
                genai_types.Part.from_bytes(data=image_data, mime_type='image/jpeg'),
                SYSTEM_PROMPT
            ]
        )
        simplified_text = response.text

        await status_msg.delete()

        # 3. Отправляем текст
        await message.answer(simplified_text, parse_mode="Markdown")

        # 4. Генерация голоса
        voice_status = await message.answer("🔊 *Озвучиваю инструкцию...*", parse_mode="Markdown")
        audio_filename = f"voice_{message.from_user.id}.mp3"

        communicate = edge_tts.Communicate(simplified_text, "ru-RU-DmitryNeural")
        await communicate.save(audio_filename)

        voice_file = FSInputFile(audio_filename)
        await message.answer_voice(voice=voice_file)

        await voice_status.delete()
        if os.path.exists(audio_filename):
            os.remove(audio_filename)

    except Exception as e:
        logging.error(f"Ошибка при обработке: {e}")
        await status_msg.edit_text("❌ Не удалось разглядеть текст. Попробуй сделать фото с более близкого расстояния при хорошем свете.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
