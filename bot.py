from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import asyncio
import os

BOT_TOKEN = '7780663324:AAFdFeSgNnGMCoyrqMiEiZ78GoBaxozW21I'
REVIEW_CHANNEL_ID = -1002264433388
COUNTER_FILE = 'counter.txt'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

review_buffer = []
buffer_timeout = 3  # секунды ожидания, если пересылаются подряд несколько отзывов

# Загрузка счётчика
def load_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            return int(f.read().strip())
    return 516  # начинаем с 516

# Сохранение счётчика
def save_counter(value):
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(value))

review_counter = load_counter()
processing = False

@dp.message()
async def handle_message(message: Message):
    global review_counter, processing, review_buffer

    if not message.forward_from and not message.forward_from_chat:
        await message.answer("Перешли мне сообщение клиента, чтобы опубликовать его как отзыв.")
        return

    review_buffer.append(message)

    if not processing:
        processing = True
        await asyncio.sleep(buffer_timeout)

        count = len(review_buffer)
        if count == 1:
            review = review_buffer[0]
            caption = f"Отзыв #{review_counter}"
            await bot.send_message(chat_id=REVIEW_CHANNEL_ID, text=caption)
            await bot.forward_message(chat_id=REVIEW_CHANNEL_ID, from_chat_id=review.chat.id, message_id=review.message_id)
            await review.answer("✅ Отзыв опубликован!")
            review_counter += 1
        else:
            start = review_counter
            end = review_counter + count - 1
            caption = f"Отзыв #{'/'.join(str(i) for i in range(start, end + 1))}"
            await bot.send_message(chat_id=REVIEW_CHANNEL_ID, text=caption)
            for review in review_buffer:
                await bot.forward_message(chat_id=REVIEW_CHANNEL_ID, from_chat_id=review.chat.id, message_id=review.message_id)
            await review_buffer[0].answer(f"✅ {count} пересланных отзыва опубликовано!")
            review_counter += count

        save_counter(review_counter)
        review_buffer = []
        processing = False

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
