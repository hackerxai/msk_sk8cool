import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import *
from database import BookingDatabase
from config import ADMIN_ID, PARKS


# Логирование
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
SELECTING_PARK, SELECTING_DATE, SELECTING_TIME, SELECTING_EQUIPMENT, CONFIRMING_BOOKING = range(5)

# Инициализация базы данных
db = BookingDatabase()

# Временное хранилище для данных пользователей
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    welcome_message = f"""
🎉 *Добро пожаловать в MSK SK8COOL!* 🛹

Привет, {user.first_name}! 👋

Мы - лучшая скейтшкола в Москве, где каждый может научиться кататься на скейте и стать настоящим райдером! 

🔥 *Что вас ждет:*
• Индивидуальный подход к каждому ученику
• Профессиональные тренеры с опытом
• Современные методики обучения
• Безопасность на первом месте
• Море позитива и драйва!

Выберите, что вас интересует:
"""
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def training_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о тренировках"""
    query = update.callback_query
    await query.answer()
    
    training_message = """
🏃‍♂️ *Как проходят тренировки в MSK SK8COOL:*

⏰ **Длительность:** 60-90 минут
👥 **Группы:** 3-6 человек (индивидуальные занятия доступны)
🏆 **Уровни:** От новичка до продвинутого

📚 **Программа обучения:**
1️⃣ **Базовые навыки** - стойка, равновесие, отталкивание
2️⃣ **Простые трюки** - ollie, kickflip, shove-it
3️⃣ **Продвинутые трюки** - 360 flip, varial kickflip
4️⃣ **Стиль и техника** - грайнды, слайды, мануалы

🛡️ **Безопасность:**
• Обязательное использование защиты
• Постепенное усложнение задач
• Контроль тренера на каждом этапе

💪 **Результат:** Уже через месяц вы будете уверенно кататься!

Готовы начать обучение? 🚀
"""
    
    await query.edit_message_text(
        training_message,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def select_park(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор парка"""
    query = update.callback_query
    await query.answer()
    
    park_message = """
📍 *Выберите парк для тренировки:*

У нас есть несколько отличных локаций в разных районах Москвы. Каждый парк уникален и имеет свои особенности!
"""
    
    await query.edit_message_text(
        park_message,
        parse_mode='Markdown',
        reply_markup=get_park_selection_keyboard()
    )

async def show_park_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать информацию о выбранном парке"""
    query = update.callback_query
    await query.answer()
    
    park_id = query.data.split('_')[1]
    park_info = PARKS[park_id]
    
    park_message = f"""
🏞️ *{park_info['name']}*

📍 **Адрес:** {park_info['address']}
📝 **Описание:** {park_info['description']}

🗺️ Откройте карту, чтобы посмотреть маршрут и понять, удобно ли вам добираться.

Если этот парк вам подходит - нажмите "Выбрать этот парк" ✅
Если хотите посмотреть другие варианты - нажмите "Выбрать другой парк" 🔄
"""
    
    await query.edit_message_text(
        park_message,
        parse_mode='Markdown',
        reply_markup=get_park_info_keyboard(park_id)
    )

async def confirm_park(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение выбора парка"""
    query = update.callback_query
    await query.answer()
    
    park_id = query.data.split('_')[2]
    park_info = PARKS[park_id]
    
    # Сохраняем выбранный парк
    user_id = query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['park_id'] = park_id
    user_data[user_id]['park_name'] = park_info['name']
    
    park_message = f"""
✅ *Парк выбран: {park_info['name']}*

Теперь выберите удобную дату для тренировки. 

📅 *Доступные даты:* (запись возможна только на следующий день и далее)
"""
    
    await query.edit_message_text(
        park_message,
        parse_mode='Markdown',
        reply_markup=get_date_selection_keyboard()
    )
    
    return SELECTING_DATE

async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор даты"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "select_date":
        # Возврат к выбору даты
        await query.edit_message_text(
            "📅 Выберите удобную дату для тренировки:",
            reply_markup=get_date_selection_keyboard()
        )
        return SELECTING_DATE
    
    date_str = query.data.split('_')[1]
    
    # Сохраняем выбранную дату
    user_id = query.from_user.id
    user_data[user_id]['date'] = date_str
    
    # Парсим дату для красивого отображения
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime("%A")
        date_display = date_obj.strftime("%d.%m.%Y")
        
        day_translations = {
            'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда',
            'Thursday': 'Четверг', 'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'
        }
        
        day_ru = day_translations.get(day_name, day_name)
        
        date_message = f"""
📅 *Дата выбрана: {day_ru}, {date_display}*

Отлично! Теперь выберите удобное время для тренировки.

⏰ *Доступные временные слоты:*
"""
        
        await query.edit_message_text(
            date_message,
            parse_mode='Markdown',
            reply_markup=get_time_selection_keyboard()
        )
        
        return SELECTING_TIME
        
    except Exception as e:
        logger.error(f"Error parsing date: {e}")
        await query.edit_message_text(
            "❌ Ошибка при выборе даты. Попробуйте еще раз.",
            reply_markup=get_date_selection_keyboard()
        )
        return SELECTING_DATE

async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор времени"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "select_time":
        # Возврат к выбору времени
        await query.edit_message_text(
            "⏰ Выберите удобное время для тренировки:",
            reply_markup=get_time_selection_keyboard()
        )
        return SELECTING_TIME
    
    time_str = query.data.split('_')[1]
    
    # Сохраняем выбранное время
    user_id = query.from_user.id
    user_data[user_id]['time'] = time_str
    
    time_message = f"""
⏰ *Время выбрано: {time_str}*

Отлично! Теперь давайте определимся с оборудованием.

🛡️ **Защита:** шлем, наколенники, налокотники, защита запястий
🛹 **Скейтборд:** если у вас нет своего

Что вам понадобится для тренировки?
"""
    
    await query.edit_message_text(
        time_message,
        parse_mode='Markdown',
        reply_markup=get_equipment_keyboard()
    )
    
    return SELECTING_EQUIPMENT

async def select_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор оборудования"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "select_equipment":
        # Возврат к выбору оборудования
        await query.edit_message_text(
            "🛡️ Выберите нужное оборудование:",
            reply_markup=get_equipment_keyboard()
        )
        return SELECTING_EQUIPMENT
    
    equipment_map = {
        'equipment_protection': 'Защита',
        'equipment_skateboard': 'Скейтборд',
        'equipment_both': 'Защита + Скейтборд',
        'equipment_none': 'Ничего не нужно'
    }
    
    equipment = equipment_map.get(query.data, 'Не указано')
    
    # Сохраняем выбранное оборудование
    user_id = query.from_user.id
    user_data[user_id]['equipment'] = equipment
    
    # Формируем сводку записи
    park_name = user_data[user_id]['park_name']
    date = user_data[user_id]['date']
    time = user_data[user_id]['time']
    
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date_display = date_obj.strftime("%d.%m.%Y")
    except:
        date_display = date
    
    summary_message = f"""
📋 *Сводка записи на тренировку:*

🏞️ **Парк:** {park_name}
📅 **Дата:** {date_display}
⏰ **Время:** {time}
🛡️ **Оборудование:** {equipment}

💰 **Стоимость:** 1500₽ за занятие
⏱️ **Длительность:** 60-90 минут

Все верно? Если да - подтвердите запись! ✅
"""
    
    await query.edit_message_text(
        summary_message,
        parse_mode='Markdown',
        reply_markup=get_confirmation_keyboard()
    )
    
    return CONFIRMING_BOOKING

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение записи"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_name = query.from_user.first_name or query.from_user.username or "Пользователь"
    
    if query.data == "confirm_booking":
        # Создаем запись в базе данных
        booking_data = user_data[user_id].copy()
        booking_id = db.add_booking(user_id, user_name, booking_data)
        
        # Отправляем уведомление админу
        admin_message = f"""
🔔 *Новая заявка на тренировку!*

👤 **Пользователь:** {user_name} (ID: {user_id})
🏞️ **Парк:** {booking_data['park_name']}
📅 **Дата:** {booking_data['date']}
⏰ **Время:** {booking_data['time']}
🛡️ **Оборудование:** {booking_data['equipment']}
🆔 **ID записи:** {booking_id}

Подтвердите или отклоните запись:
"""
        
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_message,
                parse_mode='Markdown',
                reply_markup=get_admin_confirmation_keyboard(user_id, booking_data)
            )
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
        
        # Отправляем подтверждение пользователю
        success_message = f"""
🎉 *Заявка отправлена!*

Спасибо за запись на тренировку! 

📋 **Ваша заявка:**
🏞️ **Парк:** {booking_data['park_name']}
📅 **Дата:** {booking_data['date']}
⏰ **Время:** {booking_data['time']}
🛡️ **Оборудование:** {booking_data['equipment']}

⏳ **Статус:** Ожидает подтверждения тренера

Мы свяжемся с вами в ближайшее время для подтверждения записи! 

🆔 **Номер заявки:** {booking_id}

Хотите записаться еще на одну тренировку? 🚀
"""
        
        await query.edit_message_text(
            success_message,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
        # Очищаем данные пользователя
        if user_id in user_data:
            del user_data[user_id]
        
        return ConversationHandler.END
        
    elif query.data == "cancel_booking":
        # Отмена записи
        await query.edit_message_text(
            "❌ Запись отменена. Вы можете начать заново или вернуться в главное меню.",
            reply_markup=get_main_keyboard()
        )
        
        # Очищаем данные пользователя
        if user_id in user_data:
            del user_data[user_id]
        
        return ConversationHandler.END

async def about_school(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о скейтшколе"""
    query = update.callback_query
    await query.answer()
    
    about_message = """
🏫 *О скейтшколе MSK SK8COOL:*

🌟 **Наша миссия:** Сделать скейтбординг доступным для каждого!

📚 **История:** Мы обучаем скейтбордингу с 2018 года и помогли более 500 ученикам освоить этот удивительный спорт.

👨‍🏫 **Тренеры:** 
• Сертифицированные инструкторы
• Опыт катания 10+ лет
• Индивидуальный подход к каждому

🏆 **Достижения наших учеников:**
• Участие в городских соревнованиях
• Создание собственных трюков
• Развитие скейт-сообщества

💎 **Почему мы:**
• Безопасность превыше всего
• Современные методики обучения
• Дружелюбная атмосфера
• Гибкое расписание
• Доступные цены

🚀 **Присоединяйтесь к нам и станьте частью скейт-семьи!**
"""
    
    await query.edit_message_text(
        about_message,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def contact_coach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Связаться с тренером"""
    query = update.callback_query
    await query.answer()
    
    contact_message = """
📞 *Связаться с тренером:*

💬 **Telegram:** @msk_sk8cool_coach
📱 **WhatsApp:** +7 (999) 123-45-67
📧 **Email:** coach@msksk8cool.ru

⏰ **Время работы:** Пн-Вс 9:00-21:00

🔔 **Быстрый ответ:** Обычно отвечаем в течение 30 минут!

Есть вопросы по тренировкам, расписанию или оборудованию? Смело пишите! 💪
"""
    
    await query.edit_message_text(
        contact_message,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    
    await start(update, context)

# Обработчики для админа
async def admin_confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ подтверждает запись"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[2])
    
    # Находим запись пользователя
    user_bookings = db.get_user_bookings(user_id)
    if user_bookings:
        latest_booking = user_bookings[-1]  # Берем последнюю запись
        db.confirm_booking(latest_booking['id'])
        
        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"""
🎉 *Ваша заявка подтверждена!*

✅ **Статус:** Подтверждено тренером

📋 **Детали тренировки:**
🏞️ **Парк:** {latest_booking['park_name']}
📅 **Дата:** {latest_booking['date']}
⏰ **Время:** {latest_booking['time']}
🛡️ **Оборудование:** {latest_booking['equipment']}

⏰ **Напоминание:** Бот напомнит о тренировке за 2 часа!

🚀 **Готовьтесь к отличной тренировке!**

Если у вас есть вопросы, свяжитесь с тренером.
"""
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
        
        await query.edit_message_text("✅ Заявка подтверждена!")
    else:
        await query.edit_message_text("❌ Заявка не найдена!")

async def admin_reject_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ отклоняет запись"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[2])
    
    # Находим запись пользователя
    user_bookings = db.get_user_bookings(user_id)
    if user_bookings:
        latest_booking = user_bookings[-1]
        db.reject_booking(latest_booking['id'], "Отклонено тренером")
        
        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"""
❌ *Ваша заявка отклонена*

К сожалению, тренер не может провести тренировку в указанное время.

🔄 **Что делать:**
• Выберите другое время
• Выберите другой парк
• Свяжитесь с тренером для уточнения

📞 **Связаться с тренером:** @msk_sk8cool_coach

Извините за неудобства! 😔
"""
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
        
        await query.edit_message_text("❌ Заявка отклонена!")
    else:
        await query.edit_message_text("❌ Заявка не найдена!")

async def admin_contact_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ хочет связаться с пользователем"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[2])
    
    await query.edit_message_text(f"👤 ID пользователя: {user_id}\n\nСвяжитесь с ним через Telegram или используйте команду /contact_{user_id}")

async def send_reminders(context):
    """Отправка напоминаний о тренировках"""
    upcoming_bookings = db.get_upcoming_bookings(2)  # За 2 часа
    
    for booking in upcoming_bookings:
        try:
            # Уведомляем пользователя
            await context.bot.send_message(
                chat_id=booking['user_id'],
                text=f"""
⏰ *Напоминание о тренировке!*

🚨 **Через 2 часа у вас тренировка!**

📋 **Детали:**
🏞️ **Парк:** {booking['park_name']}
📅 **Дата:** {booking['date']}
⏰ **Время:** {booking['time']}
🛡️ **Оборудование:** {booking['equipment']}

🎯 **Не забудьте:**
• Взять защиту (если нужна)
• Взять скейт (если нужен)
• Прийти за 10 минут до начала
• Хорошее настроение! 😊

🚀 **Удачи на тренировке!**
"""
            )
            
            # Уведомляем админа
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"""
⏰ *Напоминание о тренировке!*

👤 **Ученик:** {booking['user_name']}
🏞️ **Парк:** {booking['park_name']}
📅 **Дата:** {booking['date']}
⏰ **Время:** {booking['time']}

Через 2 часа начинается тренировка!
"""
            )
            
        except Exception as e:
            logger.error(f"Failed to send reminder: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте еще раз или свяжитесь с тренером."
            )
    except:
        pass
