"""
Автоматические напоминания неактивным пользователям.
Отправка сообщений раз в неделю пользователям без активности.
"""
import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot

from .stats import stats_manager

logger = logging.getLogger(__name__)


class ReminderService:
    """Сервис напоминаний для неактивных пользователей."""
    
    def __init__(self, bot: Bot, check_interval_hours: int = 24, inactive_days: int = 7):
        """
        Инициализация сервиса напоминаний.
        
        Args:
            bot: Экземпляр бота
            check_interval_hours: Интервал проверки в часах (по умолчанию 24ч = раз в сутки)
            inactive_days: Количество дней неактивности для напоминания (по умолчанию 7)
        """
        self.bot = bot
        self.check_interval_hours = check_interval_hours
        self.inactive_days = inactive_days
        self.task: asyncio.Task | None = None
        self._running = False
    
    async def send_reminder(self, user_id: int) -> bool:
        """
        Отправить напоминание пользователю.
        
        Args:
            user_id: ID пользователя Telegram
        
        Returns:
            True если отправлено успешно
        """
        try:
            reminder_messages = [
                "👋 Привет! Тебя давно не было видно.\n\n"
                "Не желаешь пройти тест и проверить свои знания?\n\n"
                "Заходи скорей и жми /start! 🚀",
                
                "🧪 Эй, вспомни про наш тест-бот!\n\n"
                "Прошла уже целая неделя. Может время освежить знания?\n\n"
                "Жми /start и вперёд к новым достижениям! 💪",
                
                "📚 Давно не виделись!\n\n"
                "Система тестирования ФССП ждёт тебя.\n"
                "Проверь свои знания прямо сейчас!\n\n"
                "Команда /start для начала. ⚡",
            ]
            
            # Случайное сообщение (можно улучшить логику выбора)
            import random
            message = random.choice(reminder_messages)
            
            await self.bot.send_message(user_id, message)
            
            # Отмечаем в БД
            await stats_manager.mark_reminder_sent(user_id)
            
            logger.info(f"✅ Напоминание отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось отправить напоминание {user_id}: {e}")
            return False
    
    async def check_and_send_reminders(self):
        """Проверка неактивных пользователей и отправка напоминаний."""
        try:
            # Получаем список неактивных пользователей
            inactive_users = await stats_manager.get_inactive_users(days=self.inactive_days)
            
            if not inactive_users:
                logger.debug(f"ℹ️ Нет неактивных пользователей ({self.inactive_days} дней)")
                return
            
            logger.info(f"📨 Найдено {len(inactive_users)} неактивных пользователей")
            
            # Отправляем напоминания
            sent_count = 0
            for user_id in inactive_users:
                if await self.send_reminder(user_id):
                    sent_count += 1
                
                # Небольшая задержка между отправками (антиспам)
                await asyncio.sleep(1)
            
            logger.info(f"✅ Отправлено {sent_count}/{len(inactive_users)} напоминаний")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке напоминаний: {e}", exc_info=True)
    
    async def _reminder_loop(self):
        """Основной цикл отправки напоминаний."""
        logger.info(
            f"▶️ Сервис напоминаний запущен "
            f"(проверка каждые {self.check_interval_hours}ч, "
            f"неактивность {self.inactive_days} дней)"
        )
        
        while self._running:
            try:
                await self.check_and_send_reminders()
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле напоминаний: {e}", exc_info=True)
            
            # Ждём до следующей проверки
            await asyncio.sleep(self.check_interval_hours * 3600)
    
    async def start(self):
        """Запустить сервис напоминаний."""
        if self._running:
            logger.warning("⚠️ Сервис напоминаний уже запущен")
            return
        
        self._running = True
        self.task = asyncio.create_task(self._reminder_loop())
        logger.info("✅ Сервис напоминаний запущен")
    
    async def stop(self):
        """Остановить сервис напоминаний."""
        if not self._running:
            return
        
        self._running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("⏸️ Сервис напоминаний остановлен")
