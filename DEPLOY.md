# 🚀 Деплой MSK SK8COOL Bot с игрой

## 🌐 Railway (рекомендуется)

### 1. Подготовка:
- Создай аккаунт на [railway.app](https://railway.app)
- Подключи GitHub репозиторий

### 2. Переменные окружения в Railway:
```
BOT_TOKEN=твой_токен_бота
ADMIN_ID=твой_telegram_id
GAME_URL=https://твой-домен.railway.app/game
```

### 3. Деплой:
- Railway автоматически деплоит при push в GitHub
- Получишь URL типа: `https://твой-проект.railway.app`

## 🌐 Render

### 1. Подготовка:
- Создай аккаунт на [render.com](https://render.com)
- Подключи GitHub репозиторий

### 2. Переменные окружения в Render:
```
BOT_TOKEN=твой_токен_бота
ADMIN_ID=твой_telegram_id
GAME_URL=https://твой-проект.onrender.com/game
```

## 🌐 Heroku

### 1. Подготовка:
- Установи Heroku CLI
- Создай аккаунт на [heroku.com](https://heroku.com)

### 2. Деплой:
```bash
heroku create твой-проект
heroku config:set BOT_TOKEN=твой_токен_бота
heroku config:set ADMIN_ID=твой_telegram_id
heroku config:set GAME_URL=https://твой-проект.herokuapp.com/game
git push heroku main
```

## 🎮 После деплоя:

1. **Получи URL** твоего сервера
2. **Обнови GAME_URL** в переменных окружения
3. **Перезапусти** приложение
4. **Протестируй** бота в Telegram!

## 🔧 Локальное тестирование:

```bash
# Установи зависимости
pip install -r requirements.txt

# Создай .env файл
cp env_example.txt .env
# Отредактируй .env с твоими токенами

# Запусти бота
python main.py
```

## 🎯 Что получится:

- 🤖 **Telegram бот** с записью на тренировки
- 🎮 **Интегрированная игра** "Собака на Скейте"
- 🌐 **Веб-сервер** для игры
- 📱 **Telegram Web App** интеграция

Удачи с деплоем! 🚀
