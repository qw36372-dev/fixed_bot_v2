#!/usr/bin/env python3
"""
test_bot_main.py — Production-ready Aiogram 3.x Telegram тест-бот
11 специализаций × FSM × PDF × AntiSpam × Числовые кнопки 1️⃣2️⃣3️⃣4️⃣5️⃣
"""

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config.settings import settings
from library import AntiSpamMiddleware, ErrorHandlerMiddleware
from library.keyboards import get_main_keyboard

# Импорт всех роутеров специализаций
from specializations import (
    oupds_router, ispolniteli_router, aliment_router, doznanie_router,
    rozyisk_router, prof_router, oko_router, informatika_router,
    kadry_router, bezopasnost_router, upravlenie_router
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Глобальные переменные
bot: Bot | None = None
dp: Dispatcher | None = None


async def on_startup():
    """Инициализация при запуске бота."""
    logger.info("🚀 Бот инициализирован и готов к работе")


async def on_shutdown():
    """Корректное завершение работы бота."""
    logger.info("🛑 Завершение работы бота")
    
    # Остановка сервиса напоминаний
    reminder_service = dp.get("reminder_service")
    if reminder_service:
        try:
            await reminder_service.stop()
            logger.info("✅ Сервис напоминаний остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка остановки напоминаний: {e}")
    
    # Graceful shutdown задач
    if dp:
        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    if bot:
        await bot.session.close()
    logger.info("👋 Бот остановлен корректно")


async def main():
    """Главная функция запуска бота."""
    global bot, dp
    
    # Проверка API токена
    if not settings.api_token:
        logger.error("❌ API_TOKEN отсутствует! Установите переменную окружения API_TOKEN")
        sys.exit(1)
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=settings.api_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация событий
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Подключение middlewares
    dp.message.middleware(AntiSpamMiddleware())
    dp.callback_query.middleware(AntiSpamMiddleware())
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    logger.info("✅ Middlewares подключены")
    
    # Главный роутер с командой /start
    main_router = Router()
    
    @main_router.message(Command("start"))
    async def cmd_start(message: Message):
        """Команда /start - главное меню."""
        await message.answer(
            "🧪 <b>ФССП Тест-бот</b>\n\n"
            "Выберите специализацию для прохождения теста:",
            reply_markup=get_main_keyboard()
        )
    
    # Подключение роутеров
    dp.include_router(main_router)
    dp.include_router(oupds_router)
    dp.include_router(ispolniteli_router)
    dp.include_router(aliment_router)
    dp.include_router(doznanie_router)
    dp.include_router(rozyisk_router)
    dp.include_router(prof_router)
    dp.include_router(oko_router)
    dp.include_router(informatika_router)
    dp.include_router(kadry_router)
    dp.include_router(bezopasnost_router)
    dp.include_router(upravlenie_router)
    
    logger.info("✅ Загружено 11 роутеров специализаций")
    logger.info("🚀 Запуск polling...")
    
    # Запуск бота
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⚠️ Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}", exc_info=True)
    finally:
        await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Прервано пользователем")
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}", exc_info=True)
        sys.exit(1)
