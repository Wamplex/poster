from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio
import os

# 🔐 Токен твоего бота
BOT_TOKEN = '7780663324:AAFdFeSgNnGMCoyrqMiEiZ78GoBaxozW21I'

# 🆔 ID твоего канала
REVIEW_CHANNEL_ID = -1002264433388

# 📁 Файл со счётчиком
COUNTER_FILE = 'counter.txt'

# Загрузка счётчика
def load_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            return int(f.read().strip())
    return 1

# Сохранение счётчика
def save_counter(value):
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(value))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

review_counter = load_counter()

# Обработка пересланных сообщений
@dp.message()
async def handle_message(message: Message):
    global review_counter

    # Проверяем, что сообщение переслано
    if not message.forward_from and not message.forward_from_chat:
        await message.answer("Перешли мне сообщение клиента, чтобы опубликовать его как отзыв.")
        return

    # Формируем подпись
    text = f"Отзыв #{review_counter}"

    # Отправляем подпись и пересланное сообщение в канал
    await bot.send_message(chat_id=REVIEW_CHANNEL_ID, text=text)
    await bot.forward_message(chat_id=REVIEW_CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id)

    # Увеличиваем счётчик и сохраняем его
    review_counter += 1
    save_counter(review_counter)

    await message.answer("✅ Отзыв опубликован!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
