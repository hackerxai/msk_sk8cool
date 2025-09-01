#!/usr/bin/env python3
"""
Система напоминаний для MSK SK8COOL
"""

import logging
from datetime import datetime, timedelta
from telegram import Bot
from config import ADMIN_ID

logger = logging.getLogger(__name__)

class ReminderSystem:
    def __init__(self, bot: Bot, job_queue):
        self.bot = bot
        self.job_queue = job_queue
    
    def schedule_reminder(self, booking_data: dict):
        """Планирует напоминание за 2 часа до тренировки"""
        try:
            # Парсим дату и время тренировки
            training_date_str = booking_data.get('date')
            training_time_str = booking_data.get('time')
            
            if not training_date_str or not training_time_str:
                logger.error("Не удалось получить дату или время тренировки")
                return
            
            # Создаем datetime объект для времени тренировки
            training_datetime = datetime.strptime(f"{training_date_str} {training_time_str}", "%Y-%m-%d %H:%M")
            
            # Время напоминания (за 2 часа до тренировки)
            reminder_time = training_datetime - timedelta(hours=2)
            
            # Проверяем, что напоминание не в прошлом
            if reminder_time <= datetime.now():
                logger.warning(f"Время напоминания в прошлом: {reminder_time}")
                return
            
            # Создаем уникальный ID для задачи
            job_id = f"reminder_{booking_data.get('user_id')}_{training_date_str}_{training_time_str}"
            
            # Планируем напоминание
            self.job_queue.run_once(
                self.send_reminder,
                reminder_time,
                data=booking_data,
                name=job_id
            )
            
            logger.info(f"Напоминание запланировано на {reminder_time} для тренировки {training_datetime}")
            
        except Exception as e:
            logger.error(f"Ошибка при планировании напоминания: {e}")
    
    async def send_reminder(self, context):
        """Отправляет напоминания пользователю и админу"""
        try:
            booking_data = context.job.data
            
            user_id = booking_data.get('user_id')
            park_name = booking_data.get('park_name')
            park_link = booking_data.get('park_link')
            training_time = booking_data.get('time')
            user_name = booking_data.get('user_name')
            username = booking_data.get('username')
            
            # Сообщение для пользователя
            user_message = (
                f"⏰ *Напоминание о тренировке!*\n\n"
                f"🏂 Через 2 часа у вас тренировка!\n\n"
                f"🏞️ *Место:* {park_name}\n"
                f"⏰ *Время:* {training_time}\n"
                f"🗺️ [Открыть на карте]({park_link})\n\n"
                f"📋 Не забудьте:\n"
                f"• Удобную одежду\n"
                f"• Воду\n"
                f"• Хорошее настроение!\n\n"
                f"🚀 Удачной тренировки!"
            )
            
            # Сообщение для админа
            admin_message = (
                f"⏰ *Напоминание о тренировке!*\n\n"
                f"🏂 Через 2 часа тренировка!\n\n"
                f"👤 *Ученик:* {user_name}\n"
                f"📱 *Username:* {username}\n"
                f"🏞️ *Парк:* {park_name}\n"
                f"⏰ *Время:* {training_time}\n\n"
                f"🗺️ [Открыть на карте]({park_link})"
            )
            
            # Отправляем напоминания
            await self.bot.send_message(
                chat_id=user_id,
                text=user_message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            await self.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            logger.info(f"Напоминания отправлены для тренировки в {training_time}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания: {e}")
    
    def cancel_reminder(self, user_id: int, training_date: str, training_time: str):
        """Отменяет запланированное напоминание"""
        try:
            job_id = f"reminder_{user_id}_{training_date}_{training_time}"
            self.job_queue.get_jobs_by_name(job_id)
            
            # Удаляем все задачи с таким именем
            jobs = self.job_queue.get_jobs_by_name(job_id)
            for job in jobs:
                job.schedule_removal()
            
            logger.info(f"Напоминание отменено: {job_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при отмене напоминания: {e}")
