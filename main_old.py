import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler
from handlers import *
from config import BOT_TOKEN, ADMIN_ID
from database import BookingDatabase

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = BookingDatabase()

def send_reminders_task(context):
    """Задача отправки напоминаний"""
    try:
        from handlers import send_reminders
        # Создаем event loop для асинхронного вызова
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(send_reminders(context))
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in reminder task: {e}")



def main():
    """Основная функция"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    if not ADMIN_ID:
        logger.error("ADMIN_ID не найден в переменных окружения!")
        return
    
    logger.info("Запуск бота MSK SK8COOL...")
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    
    # Добавляем обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(training_info, pattern="^training_info$"))
    application.add_handler(CallbackQueryHandler(select_park, pattern="^select_park$"))
    application.add_handler(CallbackQueryHandler(about_school, pattern="^about_school$"))
    application.add_handler(CallbackQueryHandler(contact_coach, pattern="^contact_coach$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    
    # Обработчики для админа
    application.add_handler(CallbackQueryHandler(admin_confirm_booking, pattern="^admin_confirm_"))
    application.add_handler(CallbackQueryHandler(admin_reject_booking, pattern="^admin_reject_"))
    application.add_handler(CallbackQueryHandler(admin_contact_user, pattern="^admin_contact_"))
    
    # ConversationHandler для записи на тренировку
    from telegram.ext import ConversationHandler
    
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(select_park, pattern="^select_park$"),
            CallbackQueryHandler(confirm_park, pattern="^confirm_park_")
        ],
        states={
            SELECTING_DATE: [
                CallbackQueryHandler(select_date, pattern="^date_"),
                CallbackQueryHandler(select_date, pattern="^select_date$")
            ],
            SELECTING_TIME: [
                CallbackQueryHandler(select_time, pattern="^time_"),
                CallbackQueryHandler(select_time, pattern="^select_time$")
            ],
            SELECTING_EQUIPMENT: [
                CallbackQueryHandler(select_equipment, pattern="^equipment_"),
                CallbackQueryHandler(select_equipment, pattern="^select_equipment$")
            ],
            CONFIRMING_BOOKING: [
                CallbackQueryHandler(confirm_booking, pattern="^(confirm_booking|cancel_booking)$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(main_menu, pattern="^main_menu$"),
            CallbackQueryHandler(select_park, pattern="^select_park$")
        ]
    )
    
    application.add_handler(conv_handler)
    
    # Обработчики для парков
    application.add_handler(CallbackQueryHandler(show_park_info, pattern="^park_"))
    application.add_handler(CallbackQueryHandler(confirm_park, pattern="^confirm_park_"))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Настраиваем регулярные задачи с помощью JobQueue
    job_queue = application.job_queue
    
    # Проверяем напоминания каждый час
    job_queue.run_repeating(send_reminders_task, interval=3600, first=10)
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе! 🚀")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
