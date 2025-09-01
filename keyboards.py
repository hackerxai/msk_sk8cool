from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import PARKS, TIME_SLOTS

def get_main_keyboard():
    """Главная клавиатура"""
    keyboard = [
        [InlineKeyboardButton("🏃‍♂️ Как проходят тренировки", callback_data="training_info")],
        [InlineKeyboardButton("📍 Выбрать парк", callback_data="select_park")],
        [InlineKeyboardButton("📅 Записаться на тренировку", callback_data="book_training")],
        [InlineKeyboardButton("ℹ️ О скейтшколе", callback_data="about_school")],
        [InlineKeyboardButton("📞 Связаться с тренером", callback_data="contact_coach")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_park_selection_keyboard():
    """Клавиатура выбора парка"""
    keyboard = []
    for park_id, park_info in PARKS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{park_info['name']}", 
                callback_data=f"park_{park_id}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_park_info_keyboard(park_id):
    """Клавиатура с информацией о парке"""
    keyboard = [
        [InlineKeyboardButton("🗺️ Открыть в Яндекс.Картах", url=PARKS[park_id]['yandex_maps'])],
        [InlineKeyboardButton("✅ Выбрать этот парк", callback_data=f"confirm_park_{park_id}")],
        [InlineKeyboardButton("🔄 Выбрать другой парк", callback_data="select_park")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_date_selection_keyboard():
    """Клавиатура выбора даты"""
    from datetime import datetime, timedelta
    
    keyboard = []
    today = datetime.now()
    
    # Показываем следующие 7 дней
    for i in range(1, 8):
        date = today + timedelta(days=i)
        day_name = date.strftime("%A")
        date_str = date.strftime("%d.%m")
        
        # Переводим дни недели на русский
        day_translations = {
            'Monday': 'Пн', 'Tuesday': 'Вт', 'Wednesday': 'Ср',
            'Thursday': 'Чт', 'Friday': 'Пт', 'Saturday': 'Сб', 'Sunday': 'Вс'
        }
        
        day_ru = day_translations.get(day_name, day_name)
        keyboard.append([
            InlineKeyboardButton(
                f"{day_ru} {date_str}", 
                callback_data=f"date_{date.strftime('%Y-%m-%d')}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="select_park")])
    return InlineKeyboardMarkup(keyboard)

def get_time_selection_keyboard():
    """Клавиатура выбора времени"""
    keyboard = []
    row = []
    
    for i, time in enumerate(TIME_SLOTS):
        row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
        if len(row) == 3:  # 3 времени в ряд
            keyboard.append(row)
            row = []
    
    if row:  # Добавляем оставшиеся
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="select_date")])
    return InlineKeyboardMarkup(keyboard)

def get_equipment_keyboard():
    """Клавиатура выбора оборудования"""
    keyboard = [
        [InlineKeyboardButton("🛡️ Да, нужна защита", callback_data="equipment_protection")],
        [InlineKeyboardButton("🛹 Да, нужен скейт", callback_data="equipment_skateboard")],
        [InlineKeyboardButton("🛡️🛹 Нужно и то, и другое", callback_data="equipment_both")],
        [InlineKeyboardButton("❌ Ничего не нужно", callback_data="equipment_none")],
        [InlineKeyboardButton("🔙 Назад", callback_data="select_time")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard():
    """Клавиатура подтверждения записи"""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить запись", callback_data="confirm_booking")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_booking")],
        [InlineKeyboardButton("🔙 Назад", callback_data="select_equipment")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_confirmation_keyboard(user_id, booking_data):
    """Клавиатура для админа подтверждения записи"""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"admin_confirm_{user_id}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"admin_reject_{user_id}")],
        [InlineKeyboardButton("📞 Связаться", callback_data=f"admin_contact_{user_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)
