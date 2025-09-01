#!/usr/bin/env python3
"""
MSK SK8COOL - Минимальный тестовый бот
"""

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, ADMIN_ID
from handlers import start, training_info, about_school, contact_coach, main_menu, select_park, show_park_info, confirm_park, select_date, select_period, select_time, equipment_check, equipment_selection, confirm_booking, final_booking_confirm, booking_cancel, admin_approve, admin_reject, my_progress, leaderboard, coach_command, play_game, error_handler
from web_server import start_web_server

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def main():
    """Основная функция"""
    logger.info("🚀 Запуск бота MSK SK8COOL с игрой...")
    
    # Запускаем веб-сервер для игры
    port = int(os.getenv('PORT', 8080))
    start_web_server(port=port)
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("coach", coach_command))
    
    # Добавляем обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(training_info, pattern="^training_info$"))
    application.add_handler(CallbackQueryHandler(about_school, pattern="^about_school$"))
    application.add_handler(CallbackQueryHandler(contact_coach, pattern="^contact_coach$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(select_park, pattern="^select_park$"))
    application.add_handler(CallbackQueryHandler(show_park_info, pattern="^park_"))
    application.add_handler(CallbackQueryHandler(confirm_park, pattern="^confirm_park_"))
    application.add_handler(CallbackQueryHandler(select_date, pattern="^date_"))
    application.add_handler(CallbackQueryHandler(select_period, pattern="^period_"))
    application.add_handler(CallbackQueryHandler(select_time, pattern="^time_"))
    application.add_handler(CallbackQueryHandler(equipment_check, pattern="^equipment_(yes|no)$"))
    application.add_handler(CallbackQueryHandler(equipment_selection, pattern="^equipment_(protection|skateboard|both)$"))
    application.add_handler(CallbackQueryHandler(final_booking_confirm, pattern="^final_confirm$"))
    application.add_handler(CallbackQueryHandler(booking_cancel, pattern="^booking_cancel$"))
    application.add_handler(CallbackQueryHandler(admin_approve, pattern="^admin_approve_"))
    application.add_handler(CallbackQueryHandler(admin_reject, pattern="^admin_reject_"))
    application.add_handler(CallbackQueryHandler(my_progress, pattern="^my_progress$"))
    application.add_handler(CallbackQueryHandler(leaderboard, pattern="^leaderboard$"))
    application.add_handler(CallbackQueryHandler(play_game, pattern="^play_game$"))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("✅ Бот запущен!")
    
    try:
        application.run_polling()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
