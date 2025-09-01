// Интеграция с Telegram Web App
class TelegramGameIntegration {
    constructor() {
        this.tg = window.Telegram?.WebApp;
        this.isTelegram = !!this.tg;
        this.userData = null;
        this.init();
    }
    
    init() {
        if (this.isTelegram) {
            this.setupTelegramIntegration();
        }
    }
    
    setupTelegramIntegration() {
        // Инициализация Telegram Web App
        this.tg.ready();
        this.tg.expand();
        
        // Получение данных пользователя
        this.userData = this.tg.initDataUnsafe?.user;
        
        // Настройка темы
        this.setupTheme();
        
        // Настройка кнопки главного меню
        this.setupMainButton();
        
        // Обработка событий
        this.setupEventListeners();
        
        console.log('Telegram Web App integration initialized');
    }
    
    setupTheme() {
        if (this.tg.colorScheme === 'dark') {
            document.body.classList.add('telegram-dark');
        } else {
            document.body.classList.add('telegram-light');
        }
        
        // Применение цветов Telegram
        if (this.tg.themeParams) {
            const root = document.documentElement;
            root.style.setProperty('--tg-bg-color', this.tg.themeParams.bg_color || '#000000');
            root.style.setProperty('--tg-text-color', this.tg.themeParams.text_color || '#00ff41');
            root.style.setProperty('--tg-button-color', this.tg.themeParams.button_color || '#00ff41');
            root.style.setProperty('--tg-button-text-color', this.tg.themeParams.button_text_color || '#000000');
        }
    }
    
    setupMainButton() {
        this.tg.MainButton.setText('🏆 Таблица лидеров');
        this.tg.MainButton.onClick(() => {
            this.showLeaderboard();
        });
    }
    
    setupEventListeners() {
        // Обработка закрытия приложения
        this.tg.onEvent('viewportChanged', () => {
            this.tg.expand();
        });
        
        // Обработка нажатия кнопки "Назад"
        this.tg.BackButton.onClick(() => {
            this.tg.close();
        });
    }
    
    // Отправка счета в бота
    sendScore(score, gameData = {}) {
        if (!this.isTelegram) return;
        
        const data = {
            action: 'game_score',
            score: score,
            game: 'dog_skate',
            timestamp: Date.now(),
            ...gameData
        };
        
        this.tg.sendData(JSON.stringify(data));
        console.log('Score sent to bot:', data);
    }
    
    // Отправка события игры
    sendGameEvent(event, data = {}) {
        if (!this.isTelegram) return;
        
        const eventData = {
            action: 'game_event',
            event: event,
            game: 'dog_skate',
            timestamp: Date.now(),
            ...data
        };
        
        this.tg.sendData(JSON.stringify(eventData));
    }
    
    // Показать таблицу лидеров
    showLeaderboard() {
        this.tg.sendData(JSON.stringify({
            action: 'show_leaderboard',
            game: 'dog_skate'
        }));
    }
    
    // Поделиться результатом
    shareResult(score) {
        this.tg.sendData(JSON.stringify({
            action: 'share_result',
            score: score,
            game: 'dog_skate'
        }));
    }
    
    // Получить данные пользователя
    getUserData() {
        return this.userData;
    }
    
    // Проверить, запущено ли в Telegram
    isTelegramApp() {
        return this.isTelegram;
    }
    
    // Показать уведомление
    showAlert(message) {
        if (this.isTelegram) {
            this.tg.showAlert(message);
        } else {
            alert(message);
        }
    }
    
    // Показать подтверждение
    showConfirm(message) {
        if (this.isTelegram) {
            this.tg.showConfirm(message);
        } else {
            return confirm(message);
        }
    }
    
    // Закрыть приложение
    close() {
        if (this.isTelegram) {
            this.tg.close();
        }
    }
}

// Расширение основной игры для работы с Telegram
class TelegramDogSkateGame extends DogSkateGame {
    constructor() {
        super();
        this.telegram = new TelegramGameIntegration();
        this.setupTelegramFeatures();
    }
    
    setupTelegramFeatures() {
        // Отправляем событие начала игры
        this.telegram.sendGameEvent('game_started');
        
        // Показываем кнопку главного меню
        if (this.telegram.isTelegramApp()) {
            this.telegram.tg.MainButton.show();
        }
    }
    
    startGame() {
        super.startGame();
        this.telegram.sendGameEvent('game_started');
    }
    
    onGameOver() {
        // Этот метод вызывается ПОСЛЕ того, как основная игра закончилась
        
        // Отправляем финальный счет
        this.telegram.sendScore(this.score, {
            obstacles_avoided: this.obstacles.length,
            game_duration: Date.now() - this.gameStartTime
        });
        
        // Показываем кнопку "Поделиться"
        if (this.telegram.isTelegramApp()) {
            this.telegram.tg.MainButton.setText('📤 Поделиться результатом');
            this.telegram.tg.MainButton.onClick(() => {
                this.telegram.shareResult(this.score);
            });
        }
    }
    

}

// Инициализация игры с поддержкой Telegram
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, запущено ли в Telegram
    if (window.Telegram?.WebApp) {
        new TelegramDogSkateGame();
    } else {
        new DogSkateGame();
    }
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TelegramGameIntegration, TelegramDogSkateGame };
}
