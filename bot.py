from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
import os
import time

# 🔐 Токен твоего бота
BOT_TOKEN = '7780663324:AAFdFeSgNnGMCoyrqMiEiZ78GoBaxozW21I'

# 🆔 ID твоего канала
REVIEW_CHANNEL_ID = -1002264433388

# 📁 Файл со счётчиком
COUNTER_FILE = 'counter.txt'

# 🧠 Временное хранилище сообщений
recent_messages = []

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

# Обработка пересланных сообщений
@dp.message()
async def handle_message(message: Message):
    if not message.forward_from and not message.forward_from_chat:
        await message.answer("Перешли мне сообщение клиента, чтобы опубликовать его как отзыв.")
        return

    current = load_counter()
    timestamp = time.time()

    # Добавляем сообщение в буфер
    recent_messages.append((message, current, timestamp))

    # Ждем немного: может это серия отзывов
    await asyncio.sleep(0.5)

    # Выбираем все сообщения из серии
    batch = [m for m, c, t in recent_messages if abs(t - timestamp) < 1.5]

    # Если это последняя из серии
    if len(batch) > 1 and message == batch[-1]:
        for i, (msg, count, _) in enumerate(batch):
            await bot.send_message(REVIEW_CHANNEL_ID, f"Отзыв #{current}/{current + len(batch) - 1}")
            await bot.forward_message(REVIEW_CHANNEL_ID, from_chat_id=msg.chat.id, message_id=msg.message_id)
        await message.answer(f"{len(batch)} пересланных отзыва")
        save_counter(current + len(batch))
        recent_messages.clear()
    elif len(batch) == 1:
        await bot.send_message(REVIEW_CHANNEL_ID, f"Отзыв #{current}")
        await bot.forward_message(REVIEW_CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        await message.answer("Пересланный отзыв")
        save_counter(current + 1)
        recent_messages.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
