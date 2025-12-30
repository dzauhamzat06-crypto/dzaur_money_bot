import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import config
from database import db

# Импортируем роутеры
from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.tasks import router as tasks_router
from handlers.referrals import router as referrals_router
from handlers.withdraw import router as withdraw_router

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Подключение роутеров
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(tasks_router)
    dp.include_router(referrals_router)
    dp.include_router(withdraw_router)
    
    # Создание таблиц БД
    await db.create_tables()
    
    # Добавление тестового задания (для примера)
    try:
        await db.add_task(
            title="Подписка на канал",
            description="Подпишитесь на наш канал и оставайтесь подписанным 7 дней",
            reward=5.0,
            category="subscribe",
            url="https://t.me/your_channel",
            max_completions=1000
        )
    except Exception as e:
        logging.info(f"Тестовое задание не добавлено (возможно уже есть): {e}")
    
    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
