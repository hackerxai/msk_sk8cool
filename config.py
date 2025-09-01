import os
from dotenv import load_dotenv

load_dotenv()

# Основные настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

# Настройки парков
PARKS = {
    'park1': {
        'name': 'Скейт-парк у м. Новопеределкино 🏞️',
        'yandex_maps': 'https://yandex.ru/maps/-/CLEzyRJy'
    },
    'park2': {
        'name': 'Скейт-парк у м. Тропарево 🌅',
        'yandex_maps': 'https://yandex.ru/maps/-/CLEz5Zo9'
    },
    'park3': {
        'name': 'Скейт-парк у м. Академика Янгеля 🌆',
        'yandex_maps': 'https://yandex.ru/maps/-/CLEz5XkA'
    },
    'park4': {
        'name': 'Скейт-парк у м. Сокольники ❄️',
        'yandex_maps': 'https://yandex.ru/maps/-/CLEzB-~h'
    }
}

# Временные слоты (интервал 2 часа)
TIME_SLOTS = [
    '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'
]

# Периоды дня
DAY_PERIODS = {
    'day': {
        'name': '☀️ День',
        'times': ['12:00', '14:00', '16:00']
    },
    'evening': {
        'name': '🌙 Вечер',
        'times': ['18:00', '20:00', '22:00']
    }
}

# Дни недели
WEEKDAYS = {
    0: 'Понедельник',
    1: 'Вторник', 
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье'
}
