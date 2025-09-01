#!/usr/bin/env python3
"""
Тест создания Application
"""

import logging
from telegram.ext import Application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_application():
    """Тестируем создание Application"""
    try:
        logger.info("🔧 Тестируем создание Application...")
        
        # Создаем приложение
        app = Application.builder().token("TEST").build()
        logger.info("✅ Application создан успешно!")
        
        # Проверяем job_queue
        job_queue = app.job_queue
        logger.info("✅ JobQueue получен успешно!")
        
        logger.info("🎉 Все тесты пройдены! Application работает!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        logger.error(f"Тип ошибки: {type(e)}")
        return False

if __name__ == "__main__":
    test_application()

