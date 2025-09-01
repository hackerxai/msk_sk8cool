#!/usr/bin/env python3
"""
Скрипт проверки готовности к запуску бота MSK SK8COOL
"""

import os
import sys
import importlib
from pathlib import Path

def check_python_version():
    """Проверка версии Python"""
    print("🐍 Проверка версии Python...")
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше!")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_files():
    """Проверка наличия необходимых файлов"""
    print("\n📁 Проверка файлов...")
    
    required_files = [
        'main.py',
        'config.py',
        'handlers.py',
        'keyboards.py',
        'database.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - НЕ НАЙДЕН!")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    return True

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    required_packages = [
        'telegram',
        'dotenv',
        'schedule'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - НЕ УСТАНОВЛЕН!")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("💡 Установите их командой: pip install -r requirements.txt")
        return False
    
    return True

def check_env_variables():
    """Проверка переменных окружения"""
    print("\n🌍 Проверка переменных окружения...")
    
    # Загружаем .env файл если он есть
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Файл .env найден")
        
        # Читаем содержимое
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие ключевых переменных
        if 'BOT_TOKEN' in content:
            print("✅ BOT_TOKEN найден в .env")
        else:
            print("❌ BOT_TOKEN НЕ НАЙДЕН в .env")
            return False
        
        if 'ADMIN_ID' in content:
            print("✅ ADMIN_ID найден в .env")
        else:
            print("❌ ADMIN_ID НЕ НАЙДЕН в .env")
            return False
        
        return True
    else:
        print("❌ Файл .env НЕ НАЙДЕН!")
        print("💡 Создайте файл .env на основе env_example.txt")
        return False

def check_config():
    """Проверка конфигурации"""
    print("\n⚙️ Проверка конфигурации...")
    
    try:
        from config import BOT_TOKEN, ADMIN_ID, PARKS, TIME_SLOTS
        
        if BOT_TOKEN and BOT_TOKEN != "your_bot_token_here":
            print("✅ BOT_TOKEN загружен")
        else:
            print("❌ BOT_TOKEN не загружен или не настроен")
            return False
        
        if ADMIN_ID and ADMIN_ID != 0:
            print("✅ ADMIN_ID загружен")
        else:
            print("❌ ADMIN_ID не загружен или не настроен")
            return False
        
        if PARKS:
            print(f"✅ Настроено парков: {len(PARKS)}")
        else:
            print("❌ Парки не настроены")
            return False
        
        if TIME_SLOTS:
            print(f"✅ Настроено временных слотов: {len(TIME_SLOTS)}")
        else:
            print("❌ Временные слоты не настроены")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке конфигурации: {e}")
        return False

def check_database():
    """Проверка базы данных"""
    print("\n🗄️ Проверка базы данных...")
    
    try:
        from database import BookingDatabase
        
        db = BookingDatabase()
        print("✅ База данных инициализирована")
        
        # Проверяем создание тестовой записи
        test_booking = db.add_booking(12345, "Test User", {
            'park_name': 'Test Park',
            'date': '2024-01-01',
            'time': '10:00',
            'equipment': 'Test Equipment'
        })
        
        if test_booking:
            print("✅ Тестовая запись создана")
            
            # Удаляем тестовую запись
            db.bookings.pop(test_booking, None)
            db.save_bookings()
            print("✅ Тестовая запись удалена")
        else:
            print("❌ Не удалось создать тестовую запись")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 Проверка готовности к запуску бота MSK SK8COOL")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_files,
        check_dependencies,
        check_env_variables,
        check_config,
        check_database
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
            break
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 Все проверки пройдены! Бот готов к запуску!")
        print("\n💡 Для запуска выполните:")
        print("   python main.py")
    else:
        print("❌ Обнаружены проблемы! Исправьте их перед запуском.")
        print("\n💡 Проверьте:")
        print("   - Установлены ли все зависимости")
        print("   - Настроен ли файл .env")
        print("   - Все ли файлы на месте")
    
    return all_passed

if __name__ == "__main__":
    main()
