#!/usr/bin/env python3
"""
MSK SK8COOL - Обработчики команд бота
"""

import logging
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from config import PARKS, TIME_SLOTS, DAY_PERIODS, ADMIN_ID
from reminders import ReminderSystem
from progress import ProgressSystem

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие и главное меню"""
    # Проверяем, есть ли параметр в команде start
    if context.args and context.args[0] == "msk_sk8cool":
        # Пользователь перешел по ссылке из бота
        user = update.effective_user
        user_name = user.first_name
        username = user.username or "Не указан"
        user_id = user.id
        
        welcome_message = (
            f"👋 *Привет! Хочу записаться на тренировку!*\n\n"
            f"👤 *Имя:* {user_name}\n"
            f"📱 *Username:* @{username}\n"
            f"🆔 *ID:* {user_id}\n\n"
            f"🏂 *Школа:* MSK SK8COOL\n"
            f"📅 *Дата обращения:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"💬 Пользователь хочет связаться с тренером для записи на тренировку!"
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )
        
        # Отправляем дополнительную информацию
        await update.message.reply_text(
            "🎯 *Отлично! Я помогу вам записаться на тренировку!*\n\n"
            "🏂 *Что у нас есть:*\n"
            "• Групповые занятия 2-4 человека\n"
            "• Индивидуальные тренировки\n"
            "• Занятия в лучших парках Москвы\n"
            "• Опытные тренеры с сертификатами\n\n"
            "💰 *Стоимость:*\n"
            "• Групповое занятие: 2000₽/2 часа\n"
            "• Индивидуальное: 3000₽/1.5 часа\n"
            "• Аренда защиты: +500₽\n"
            "• Аренда скейтборда: +500₽\n\n"
            "📅 *Когда хотите начать?*\n"
            "Запишитесь через нашего бота @msk_sk8cool_bot или скажите, когда вам удобно!",
            parse_mode='Markdown'
        )
        return
    elif context.args and context.args[0] == "training":
        # Пользователь перешел по ссылке для записи на тренировку
        await training_info(update, context)
        return
    elif context.args and context.args[0] == "game":
        # Пользователь перешел по ссылке для игры
        await play_game(update, context)
        return
    
    # Обычное приветствие
    keyboard = [
        [InlineKeyboardButton("🏂 Записаться на тренировку", callback_data="training_info")],
        [InlineKeyboardButton("🎮 Играть в игру", callback_data="play_game")],
        [InlineKeyboardButton("📊 Мой прогресс", callback_data="my_progress")],
        [InlineKeyboardButton("🏆 Таблица лидеров", callback_data="leaderboard")],
        [InlineKeyboardButton("🏫 О школе", callback_data="about_school")],
        [InlineKeyboardButton("📞 Связаться с тренером", callback_data="contact_coach")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛹 *Добро пожаловать в MSK SK8COOL!*\n\n"
        "Мы - школа скейтбординга в Москве! 🏂\n"
        "Выберите, что вас интересует:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def training_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о тренировках"""
    await update.callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📍 Выбрать парк", callback_data="select_park")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🏂 *Как проходят тренировки:*\n\n"
        "• Групповые занятия 2-4 человека\n"
        "• Индивидуальные тренировки\n"
        "• Длительность: 1-1.5 часа\n"
        "• Опытные тренеры с сертификатами\n"
        "• Все уровни: от новичков до продвинутых\n\n"
        "Давайте выберем парк для тренировки! 🎯",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def about_school(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о школе"""
    await update.callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🏫 *О школе MSK SK8COOL:*\n\n"
        "Мы обучаем скейтбордингу с 2020 года! 🎓\n\n"
        "• Более 500 учеников\n"
        "• 5+ опытных тренеров\n"
        "• Занятия в лучших парках Москвы\n"
        "• Безопасность превыше всего\n"
        "• Индивидуальный подход к каждому\n\n"
        "Присоединяйтесь к нашей команде! 🚀",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def contact_coach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Контакты тренера"""
    await update.callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💬 Написать тренеру", url="https://t.me/wip_sxiueohd?start=msk_sk8cool")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "📞 *Связаться с тренером:*\n\n"
        "Нажмите кнопку ниже, чтобы открыть чат с тренером!\n\n"
        "⏰ *Время работы:* 9:00 - 21:00\n"
        "⚡ *Ответим в течение 30 минут!*\n\n"
        "При нажатии откроется чат с автоматическим приветственным сообщением! 🚀",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    await update.callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🏂 Записаться на тренировку", callback_data="training_info")],
        [InlineKeyboardButton("🎮 Играть в игру", callback_data="play_game")],
        [InlineKeyboardButton("📊 Мой прогресс", callback_data="my_progress")],
        [InlineKeyboardButton("🏆 Таблица лидеров", callback_data="leaderboard")],
        [InlineKeyboardButton("🏫 О школе", callback_data="about_school")],
        [InlineKeyboardButton("📞 Связаться с тренером", callback_data="contact_coach")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🛹 *MSK SK8COOL - Главное меню*\n\n"
        "Выберите, что вас интересует:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def select_park(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор парка"""
    await update.callback_query.answer()
    
    keyboard = []
    for park_id, park_info in PARKS.items():
        keyboard.append([InlineKeyboardButton(
            f"📍 {park_info['name']}", 
            callback_data=f"park_{park_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "📍 *Выберите парк для тренировки:*\n\n"
        "У нас есть несколько отличных локаций в разных районах Москвы! 🏞️",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_park_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать информацию о парке"""
    await update.callback_query.answer()
    
    park_id = update.callback_query.data.split('_')[1]
    park_info = PARKS[park_id]
    
    keyboard = [
        [InlineKeyboardButton("🗺️ Открыть карту", url=park_info['yandex_maps'])],
        [InlineKeyboardButton("✅ Выбрать этот парк", callback_data=f"confirm_park_{park_id}")],
        [InlineKeyboardButton("🔄 Выбрать другой парк", callback_data="select_park")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"🏞️ *{park_info['name']}*\n\n"
        f"🗺️ Откройте карту, чтобы посмотреть маршрут!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def confirm_park(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение выбора парка"""
    await update.callback_query.answer()
    
    park_id = update.callback_query.data.split('_')[2]
    park_info = PARKS[park_id]
    
    # Сохраняем выбранный парк в контексте пользователя
    user_id = update.callback_query.from_user.id
    if 'user_data' not in context.user_data:
        context.user_data['user_data'] = {}
    context.user_data['user_data']['park_id'] = park_id
    context.user_data['user_data']['park_name'] = park_info['name']
    
    # Создаем кнопки для выбора даты (7 дней вперед)
    keyboard = []
    today = datetime.now()
    
    for i in range(1, 8):  # Следующие 7 дней
        future_date = today + timedelta(days=i)
        day_name = future_date.strftime("%A")
        day_number = future_date.strftime("%d")
        month_name = future_date.strftime("%B")
        
        # Перевод дней недели
        day_translations = {
            'Monday': 'Пн', 'Tuesday': 'Вт', 'Wednesday': 'Ср', 'Thursday': 'Чт',
            'Friday': 'Пт', 'Saturday': 'Сб', 'Sunday': 'Вс'
        }
        month_translations = {
            'January': 'янв', 'February': 'фев', 'March': 'мар', 'April': 'апр',
            'May': 'май', 'June': 'июн', 'July': 'июл', 'August': 'авг',
            'September': 'сен', 'October': 'окт', 'November': 'ноя', 'December': 'дек'
        }
        
        day_ru = day_translations.get(day_name, day_name)
        month_ru = month_translations.get(month_name, month_name)
        
        if i == 1:
            emoji = "🎯"
            label = "Завтра"
        else:
            emoji = "📋"
            label = f"{day_ru}, {day_number} {month_ru}"
        
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {label}", 
            callback_data=f"date_{i}_days"
        )])
    
    keyboard.extend([
        [InlineKeyboardButton("🔄 Другой парк", callback_data="select_park")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"🎯 *Парк выбран: {park_info['name']}*\n\n"
        f"📅 *Выберите дату тренировки:*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ Запись доступна на следующий день и далее",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор даты"""
    await update.callback_query.answer()
    
    # Парсим количество дней
    parts = update.callback_query.data.split('_')
    days_ahead = int(parts[1])
    
    # Вычисляем дату
    today = datetime.now()
    selected_date = today + timedelta(days=days_ahead)
    
    # Форматируем дату для отображения
    day_name = selected_date.strftime("%A")
    day_number = selected_date.strftime("%d")
    month_name = selected_date.strftime("%B")
    
    # Перевод дней недели
    day_translations = {
        'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда', 'Thursday': 'Четверг',
        'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'
    }
    month_translations = {
        'January': 'января', 'February': 'февраля', 'March': 'марта', 'April': 'апреля',
        'May': 'мая', 'June': 'июня', 'July': 'июля', 'August': 'августа',
        'September': 'сентября', 'October': 'октября', 'November': 'ноября', 'December': 'декабря'
    }
    
    day_ru = day_translations.get(day_name, day_name)
    month_ru = month_translations.get(month_name, month_name)
    
    if days_ahead == 1:
        date_display = "Завтра"
    else:
        date_display = f"{day_ru}, {day_number} {month_ru}"
    
    # Сохраняем выбранную дату
    if 'user_data' not in context.user_data:
        context.user_data['user_data'] = {}
    context.user_data['user_data']['date'] = selected_date.strftime('%Y-%m-%d')
    context.user_data['user_data']['date_display'] = date_display
    
    # Создаем кнопки для выбора периода дня
    keyboard = [
        [InlineKeyboardButton("☀️ День", callback_data="period_day")],
        [InlineKeyboardButton("🌙 Вечер", callback_data="period_evening")],
        [InlineKeyboardButton("🔄 Другая дата", callback_data="select_park")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    park_name = context.user_data['user_data'].get('park_name', 'Парк')
    
    await update.callback_query.edit_message_text(
        f"🎯 *Парк:* {park_name}\n"
        f"📅 *Дата:* {date_display}\n\n"
        f"⏰ *Выберите период дня:*\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def select_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор периода дня"""
    await update.callback_query.answer()
    
    period = update.callback_query.data.split('_')[1]
    period_info = DAY_PERIODS[period]
    
    # Создаем кнопки для выбора времени в выбранном периоде
    keyboard = []
    for time_slot in period_info['times']:
        if period == 'day':
            emoji = "☀️"
        else:
            emoji = "🌙"
        keyboard.append([InlineKeyboardButton(f"{emoji} {time_slot}", callback_data=f"time_{time_slot}")])
    
    keyboard.extend([
        [InlineKeyboardButton("🔄 Другой период", callback_data="select_park")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    park_name = context.user_data['user_data'].get('park_name', 'Парк')
    date_display = context.user_data['user_data'].get('date_display', 'Дата')
    
    await update.callback_query.edit_message_text(
        f"🎯 *Парк:* {park_name}\n"
        f"📅 *Дата:* {date_display}\n"
        f"⏰ *Период:* {period_info['name']}\n\n"
        f"🕐 *Выберите время:*\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор времени"""
    await update.callback_query.answer()
    
    callback_data = update.callback_query.data
    if callback_data.startswith("time_header_"):
        # Это заголовок, просто отвечаем без изменений
        return
    
    time_slot = callback_data.split('_')[1]
    
    # Сохраняем выбранное время
    if 'user_data' not in context.user_data:
        context.user_data['user_data'] = {}
    context.user_data['user_data']['time'] = time_slot
    
    # Сохраняем выбранное время
    if 'user_data' not in context.user_data:
        context.user_data['user_data'] = {}
    context.user_data['user_data']['time'] = time_slot
    
    # Создаем кнопки для проверки оборудования
    keyboard = [
        [InlineKeyboardButton("✅ Да, у меня всё есть", callback_data="equipment_yes")],
        [InlineKeyboardButton("❌ Нет, нужна помощь", callback_data="equipment_no")],
        [InlineKeyboardButton("🔄 Другое время", callback_data="select_park")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    park_name = context.user_data['user_data'].get('park_name', 'Парк')
    date_display = context.user_data['user_data'].get('date_display', 'Дата')
    
    await update.callback_query.edit_message_text(
        f"🎯 *Парк:* {park_name}\n"
        f"📅 *Дата:* {date_display}\n"
        f"⏰ *Время:* {time_slot}\n\n"
        f"🛡️ *Для тренировки нужны:*\n"
        f"• Шлем\n"
        f"• Защита (наколенники, налокотники)\n"
        f"• Скейтборд\n\n"
        f"**У тебя всё есть?**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def equipment_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка оборудования"""
    await update.callback_query.answer()
    
    choice = update.callback_query.data.split('_')[1]
    
    if choice == "yes":
        # У пользователя всё есть, сохраняем это и переходим к подтверждению записи
        if 'user_data' not in context.user_data:
            context.user_data['user_data'] = {}
        context.user_data['user_data']['equipment'] = 'none'
        await confirm_booking(update, context)
    elif choice == "no":
        # Пользователю нужна помощь с оборудованием
        keyboard = [
            [InlineKeyboardButton("🛡️ Защита", callback_data="equipment_protection")],
            [InlineKeyboardButton("🛹 Скейтборд", callback_data="equipment_skateboard")],
            [InlineKeyboardButton("🛡️🛹 Защита + Скейтборд", callback_data="equipment_both")],
            [InlineKeyboardButton("🔄 Другое время", callback_data="select_park")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        park_name = context.user_data['user_data'].get('park_name', 'Парк')
        date_display = context.user_data['user_data'].get('date_display', 'Дата')
        time_slot = context.user_data['user_data'].get('time', 'Время')
        
        await update.callback_query.edit_message_text(
            f"🎯 *Парк:* {park_name}\n"
            f"📅 *Дата:* {date_display}\n"
            f"⏰ *Время:* {time_slot}\n\n"
            f"🛡️ *Что тебе нужно?*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def equipment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор оборудования"""
    await update.callback_query.answer()
    
    equipment_type = update.callback_query.data.split('_')[1]
    
    # Сохраняем выбранное оборудование
    if 'user_data' not in context.user_data:
        context.user_data['user_data'] = {}
    context.user_data['user_data']['equipment'] = equipment_type
    
    # Переходим к подтверждению записи
    await confirm_booking(update, context)

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение записи"""
    await update.callback_query.answer()
    
    user_data = context.user_data.get('user_data', {})
    park_name = user_data.get('park_name', 'Парк')
    date_display = user_data.get('date_display', 'Дата')
    time_slot = user_data.get('time', 'Время')
    equipment = user_data.get('equipment', 'none')
    
    # Определяем текст оборудования
    equipment_text = {
        'protection': '🛡️ Защита',
        'skateboard': '🛹 Скейтборд',
        'both': '🛡️🛹 Защита + Скейтборд',
        'none': '✨ У меня всё есть'
    }.get(equipment, '✨ У меня всё есть')
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить запись", callback_data="final_confirm")],
        [InlineKeyboardButton("❌ Отменить", callback_data="booking_cancel")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"🎯 *Подтверждение записи*\n\n"
        f"🏞️ *Парк:* {park_name}\n"
        f"📅 *Дата:* {date_display}\n"
        f"⏰ *Время:* {time_slot}\n"
        f"🛡️ *Оборудование:* {equipment_text}\n\n"
        f"💰 *Стоимость:* 1500₽\n"
        f"⏱️ *Длительность:* 60-90 минут\n\n"
        f"**Всё верно?**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def final_booking_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финальное подтверждение записи"""
    await update.callback_query.answer()
    
    # Отладочная информация
    logger.info(f"Context user_data: {context.user_data}")
    
    user_data = context.user_data.get('user_data', {})
    logger.info(f"User data: {user_data}")
    
    park_name = user_data.get('park_name', 'Парк')
    date_display = user_data.get('date_display', 'Дата')
    time_slot = user_data.get('time', 'Время')
    equipment = user_data.get('equipment', 'none')
    
    logger.info(f"Extracted data - Park: {park_name}, Date: {date_display}, Time: {time_slot}, Equipment: {equipment}")
    
    # Определяем текст оборудования
    equipment_text = {
        'protection': '🛡️ Защита',
        'skateboard': '🛹 Скейтборд',
        'both': '🛡️🛹 Защита + Скейтборд',
        'none': '✨ У меня всё есть'
    }.get(equipment, '✨ У меня всё есть')
    
    # Отправляем уведомление админу
    username = update.callback_query.from_user.username
    username_text = f"@{username}" if username else "Не указан"
    
    admin_message = (
        f"🎯 *Новая заявка на тренировку!*\n\n"
        f"👤 *Пользователь:* {update.callback_query.from_user.first_name}\n"
        f"🆔 *ID:* {update.callback_query.from_user.id}\n"
        f"📱 *Username:* {username_text}\n"
        f"🏞️ *Парк:* {park_name}\n"
        f"📅 *Дата:* {date_display}\n"
        f"⏰ *Время:* {time_slot}\n"
        f"🛡️ *Оборудование:* {equipment_text}\n\n"
        f"💰 *Стоимость:* 1500₽"
    )
    
    # Создаем кнопки для админа с данными о парке
    park_id = user_data.get('park_id', 'park1')
    training_date = user_data.get('date', '')
    training_time = user_data.get('time', '')
    
    admin_keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"admin_approve_{update.callback_query.from_user.id}_{park_id}_{training_date}_{training_time}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"admin_reject_{update.callback_query.from_user.id}_{park_id}_{training_date}_{training_time}")]
    ]
    admin_reply_markup = InlineKeyboardMarkup(admin_keyboard)
    
    try:
        # Отправляем сообщение админу с кнопками
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            reply_markup=admin_reply_markup,
            parse_mode='Markdown'
        )
        
        # Подтверждаем пользователю
        keyboard = [
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"🎉 *Заявка отправлена!*\n\n"
            f"✅ Ваша заявка на тренировку отправлена тренеру.\n"
            f"📱 Ожидайте подтверждения в ближайшее время.\n\n"
            f"🏞️ *Парк:* {park_name}\n"
            f"📅 *Дата:* {date_display}\n"
            f"⏰ *Время:* {time_slot}\n"
            f"🛡️ *Оборудование:* {equipment_text}\n\n"
            f"💰 *Стоимость:* 1500₽",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления админу: {e}")
        await update.callback_query.edit_message_text(
            "❌ Произошла ошибка при отправке заявки. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ подтверждает заявку"""
    await update.callback_query.answer()
    
    # Проверяем, что это админ
    if update.callback_query.from_user.id != ADMIN_ID:
        await update.callback_query.edit_message_text("❌ У вас нет прав для этого действия.")
        return
    
    # Извлекаем данные из callback_data
    parts = update.callback_query.data.split('_')
    user_id = parts[2]
    park_id = parts[3] if len(parts) > 3 else 'park1'
    training_date = parts[4] if len(parts) > 4 else ''
    training_time = parts[5] if len(parts) > 5 else ''
    
    # Получаем данные о парке
    park_info = PARKS.get(park_id, PARKS['park1'])
    park_name = park_info['name']
    park_link = park_info['yandex_maps']
    
    # Обновляем сообщение админа
    await update.callback_query.edit_message_text(
        f"✅ *Заявка подтверждена!*\n\n"
        f"👤 Пользователь ID: {user_id}\n"
        f"🏞️ Парк: {park_name}\n"
        f"📅 Заявка одобрена тренером\n"
        f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        parse_mode='Markdown'
    )
    
    # Отправляем уведомление пользователю
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 *Ваша заявка подтверждена!*\n\n"
                 f"✅ Тренер подтвердил вашу заявку на тренировку.\n"
                 f"📱 Ждем вас в назначенное время!\n\n"
                 f"🏞️ *Место встречи:* {park_name}\n"
                 f"🗺️ [Открыть на карте]({park_link})\n\n"
                 f"📋 Не забудьте взять с собой:\n"
                 f"• Хорошее настроение\n"
                 f"• Удобную одежду\n"
                 f"• Воду\n\n"
                 f"🚀 Удачной тренировки!",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        # Планируем напоминание за 2 часа до тренировки
        reminder_system = ReminderSystem(context.bot, context.job_queue)
        
        # Собираем данные для напоминания
        booking_data = {
            'user_id': int(user_id),
            'user_name': update.callback_query.from_user.first_name,
            'username': f"@{update.callback_query.from_user.username}" if update.callback_query.from_user.username else "Не указан",
            'park_name': park_name,
            'park_link': park_link,
            'date': training_date,
            'time': training_time
        }
        
        # Планируем напоминание
        reminder_system.schedule_reminder(booking_data)
        
        # Обновляем прогресс пользователя
        try:
            progress_system = ProgressSystem()
            
            # Получаем информацию о пользователе
            user_info = await context.bot.get_chat(int(user_id))
            user_name = user_info.first_name
            username = user_info.username or "Не указан"
            
            # Добавляем тренировку в прогресс
            progress_result = progress_system.add_session(
                user_id=int(user_id),
                user_name=user_name,
                username=username,
                park_name=park_name,
                session_date=training_date,
                session_time=training_time
            )
            
            # Если есть новые достижения, отправляем уведомление
            if progress_result['new_achievements']:
                achievements_text = "\n".join([
                    f"🏆 {achievement['name']}: {achievement['description']}"
                    for achievement in progress_result['new_achievements']
                ])
                
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=f"🎉 *Новые достижения!*\n\n{achievements_text}\n\n"
                         f"Продолжайте в том же духе! 🚀",
                    parse_mode='Markdown'
                )
            
            # Отправляем обновленный прогресс
            progress_message = progress_system.format_progress_message(int(user_id))
            await context.bot.send_message(
                chat_id=int(user_id),
                text=progress_message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении прогресса: {e}")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления пользователю: {e}")

async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ отклоняет заявку"""
    await update.callback_query.answer()
    
    # Проверяем, что это админ
    if update.callback_query.from_user.id != ADMIN_ID:
        await update.callback_query.edit_message_text("❌ У вас нет прав для этого действия.")
        return
    
    # Извлекаем данные из callback_data
    parts = update.callback_query.data.split('_')
    user_id = parts[2]
    park_id = parts[3] if len(parts) > 3 else 'park1'
    training_date = parts[4] if len(parts) > 4 else ''
    training_time = parts[5] if len(parts) > 5 else ''
    
    # Получаем данные о парке
    park_info = PARKS.get(park_id, PARKS['park1'])
    park_name = park_info['name']
    
    # Обновляем сообщение админа
    await update.callback_query.edit_message_text(
        f"❌ *Заявка отклонена!*\n\n"
        f"👤 Пользователь ID: {user_id}\n"
        f"🏞️ Парк: {park_name}\n"
        f"📅 Заявка отклонена тренером\n"
        f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        parse_mode='Markdown'
    )
    
    # Отправляем уведомление пользователю
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ *Заявка отклонена*\n\n"
                 "К сожалению, ваша заявка на тренировку была отклонена.\n"
                 "Возможные причины:\n"
                 "• Занятое время\n"
                 "• Недоступность тренера\n"
                 "• Технические работы\n\n"
                 "🔄 Попробуйте выбрать другое время или свяжитесь с тренером.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления пользователю: {e}")

async def booking_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена записи"""
    await update.callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "❌ Запись отменена.\n\n"
        "Можете начать заново или вернуться в главное меню.",
        reply_markup=reply_markup
    )

async def my_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать прогресс пользователя"""
    await update.callback_query.answer()
    
    try:
        progress_system = ProgressSystem()
        user_id = update.callback_query.from_user.id
        
        progress_message = progress_system.format_progress_message(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🏆 Таблица лидеров", callback_data="leaderboard")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            progress_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении прогресса: {e}")
        await update.callback_query.edit_message_text(
            "❌ Ошибка при получении прогресса. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
            ]])
        )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать таблицу лидеров"""
    await update.callback_query.answer()
    
    try:
        progress_system = ProgressSystem()
        leaderboard_message = progress_system.format_leaderboard_message(5)
        
        keyboard = [
            [InlineKeyboardButton("📊 Мой прогресс", callback_data="my_progress")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            leaderboard_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении таблицы лидеров: {e}")
        await update.callback_query.edit_message_text(
            "❌ Ошибка при получении таблицы лидеров. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
            ]])
        )

async def coach_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для быстрого доступа к тренеру"""
    keyboard = [
        [InlineKeyboardButton("💬 Написать тренеру", url="https://t.me/wip_sxiueohd?start=msk_sk8cool")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📞 *Связаться с тренером:*\n\n"
        "Нажмите кнопку ниже, чтобы открыть чат с тренером!\n\n"
        "⏰ *Время работы:* 9:00 - 21:00\n"
        "⚡ *Ответим в течение 30 минут!*\n\n"
        "При нажатии откроется чат с автоматическим приветственным сообщением! 🚀",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск игры 'Собака на Скейте'"""
    await update.callback_query.answer()
    
    # Получаем URL для игры (локально или на сервере)
    game_url = os.getenv('GAME_URL', 'https://web-production-af17e.up.railway.app/game')
    
    keyboard = [
        [InlineKeyboardButton("🎮 Играть!", web_app=WebAppInfo(url=game_url))],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎮 *Игра 'Собака на Скейте'*\n\n"
        "🐕 Управляй собакой на скейтборде!\n"
        "🛹 Прыгай через препятствия!\n"
        "🏆 Устанавливай рекорды!\n\n"
        "🎯 *Как играть:*\n"
        "• Нажми ПРОБЕЛ или кликни для прыжка\n"
        "• Избегай препятствий\n"
        "• Собирай очки!\n\n"
        "Нажми кнопку ниже, чтобы начать игру! 🚀",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def create_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание поста в канал с кнопкой записи"""
    # Проверяем, что это админ
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для этого действия.")
        return
    
    # ID канала
    channel_id = -1002879902839
    
    # Сначала проверим, может ли бот отправить сообщение в канал
    try:
        test_message = "🧪 Тест отправки сообщения"
        await context.bot.send_message(
            chat_id=channel_id,
            text=test_message
        )
        await update.message.reply_text("✅ Бот может отправлять сообщения в канал!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка доступа к каналу: {e}")
        await update.message.reply_text("🔧 Решение:\n1. Добавь бота @msk_sk8coolbot в канал как администратора\n2. Дай права на отправку сообщений\n3. Попробуй команду /post снова")
        return
    
    # Создаем кнопку для записи
    keyboard = [
        [InlineKeyboardButton("🏂 Записаться на тренировку", url="https://t.me/msk_sk8coolbot?start=training")],
        [InlineKeyboardButton("🎮 Играть в игру", url="https://t.me/msk_sk8coolbot?start=game")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Текст поста
    post_text = """
🛹 *MSK SK8COOL - Школа скейтбординга!*

🏂 *Записывайся на тренировки:*
• Групповые занятия 2-4 человека
• Индивидуальные тренировки  
• Опытные тренеры с сертификатами
• Занятия в лучших парках Москвы

🎮 *А еще у нас есть крутая игра!*
Попробуй управлять собакой на скейтборде!

💰 *Стоимость:* 1500₽ за занятие
⏱️ *Длительность:* 60-90 минут

👇 *Нажми кнопку ниже для записи!*
"""
    
    try:
        await context.bot.send_message(
            chat_id=channel_id,
            text=post_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await update.message.reply_text("✅ Пост успешно отправлен в канал!")
    except Exception as e:
        logger.error(f"Ошибка при отправке поста в канал: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления {update}: {context.error}")
    
    try:
        if update and update.callback_query:
            await update.callback_query.answer("Произошла ошибка. Попробуйте еще раз.")
        elif update and update.message:
            await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")
    except Exception as e:
        logger.error(f"Ошибка в обработчике ошибок: {e}")
