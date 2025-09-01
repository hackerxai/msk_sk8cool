class DogSkateGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.scoreElement = document.getElementById('score');
        this.highScoreElement = document.getElementById('highScore');
        this.finalScoreElement = document.getElementById('finalScore');
        
        // Полифилл для roundRect
        if (!this.ctx.roundRect) {
            this.ctx.roundRect = function(x, y, width, height, radius) {
                this.beginPath();
                this.moveTo(x + radius, y);
                this.lineTo(x + width - radius, y);
                this.quadraticCurveTo(x + width, y, x + width, y + radius);
                this.lineTo(x + width, y + height - radius);
                this.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
                this.lineTo(x + radius, y + height);
                this.quadraticCurveTo(x, y + height, x, y + height - radius);
                this.lineTo(x, y + radius);
                this.quadraticCurveTo(x, y, x + radius, y);
                this.closePath();
            };
        }
        
        // Настройки игры
        this.gameWidth = this.canvas.width;
        this.gameHeight = this.canvas.height;
        this.groundY = this.gameHeight - 60;
        
        // Состояние игры
        this.gameRunning = false;
        this.gamePaused = false;
        this.score = 0;
        this.highScore = localStorage.getItem('dogSkateHighScore') || 0;
        this.highScoreElement.textContent = this.highScore;
        
        // Игрок (собака на скейте)
        this.player = {
            x: 100,
            y: this.groundY - 40,
            width: 60,
            height: 40,
            velocityY: 0,
            isJumping: false,
            skateOffset: 0,
            justLanded: false,
            landingCooldown: 0,
            jumpAngle: 0,
            jumpScale: 1
        };
        
        // Физика
        this.gravity = 0.7;
        this.jumpPower = -16;
        
        // Препятствия
        this.obstacles = [];
        this.obstacleTypes = [
            { name: 'неоновый_барьер', width: 25, height: 50, y: this.groundY - 50 }
        ];
        
        // Скорость игры
        this.gameSpeed = 5;
        this.speedIncrease = 0.001;
        
        // Анимация
        this.animationId = null;
        this.lastTime = 0;
        
        // Фон
        this.backgroundX = 0;
        
        // Частицы
        this.particles = [];
        
        // Анимация столкновения
        this.crashAnimation = {
            active: false,
            pieces: [],
            time: 0,
            maxTime: 60,
            wasStarted: false  // Флаг: была ли запущена анимация рассыпания
        };
        
        // Звуковые эффекты (ВРЕМЕННО ОТКЛЮЧЕНЫ)
        this.sounds = {
            jump: () => {}, // Пустая функция
            land: () => {}, // Пустая функция
            crash: () => {}, // Пустая функция
            background: () => {} // Пустая функция
        };
        
        this.setupEventListeners();
        this.draw();
    }
    
    // Создание звуковых эффектов
    createJumpSound() {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        return () => {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(400, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        };
    }
    
    createLandSound() {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        return () => {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(200, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(100, audioContext.currentTime + 0.2);
            
            gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        };
    }
    
    createCrashSound() {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        return () => {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(150, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(50, audioContext.currentTime + 0.5);
            
            gainNode.gain.setValueAtTime(0.4, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        };
    }
    
    createBackgroundSound() {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        return () => {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(220, audioContext.currentTime);
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.05, audioContext.currentTime);
            
            oscillator.start(audioContext.currentTime);
            return { oscillator, gainNode };
        };
    }
    

    setupMobileControls() {
        // Определяем, мобильное ли устройство
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
            // Добавляем виртуальную кнопку прыжка для мобильных
            this.addVirtualJumpButton();
            
            // Улучшаем сенсорное управление
            this.canvas.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.handleTouchStart(e);
            });
            
            this.canvas.addEventListener('touchend', (e) => {
                e.preventDefault();
                this.handleTouchEnd(e);
            });
        }
    }
    
    addVirtualJumpButton() {
        // Создаем виртуальную кнопку прыжка
        const jumpButton = document.createElement('div');
        jumpButton.id = 'virtualJumpButton';
        jumpButton.innerHTML = '🦘';
        jumpButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #00ff41;
            border: 2px solid #000;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            cursor: pointer;
            z-index: 1000;
            user-select: none;
            box-shadow: 0 4px 8px rgba(0, 255, 65, 0.3);
        `;
        
        jumpButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (this.gameRunning && !this.gamePaused) {
                this.jump();
            }
        });
        
        jumpButton.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.gameRunning && !this.gamePaused) {
                this.jump();
            }
        });
        
        document.body.appendChild(jumpButton);
    }
    
    handleTouchStart(e) {
        // Улучшенная обработка касаний
        if (this.gameRunning && !this.gamePaused) {
            this.jump();
        }
    }
    
    handleTouchEnd(e) {
        // Обработка окончания касания
        e.preventDefault();
    }
    
    setupEventListeners() {
        // Клавиатура
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.gameRunning && !this.gamePaused) {
                e.preventDefault();
                this.jump();
            }
        });
        
        // Клики/тапы
        this.canvas.addEventListener('click', () => {
            if (this.gameRunning && !this.gamePaused) {
                this.jump();
            }
        });
        
        // Кнопки управления
        document.getElementById('startButton').addEventListener('click', () => {
            this.startGame();
        });
        
        document.getElementById('pauseButton').addEventListener('click', () => {
            this.togglePause();
        });
        
        document.getElementById('restartButton').addEventListener('click', () => {
            this.restartGame();
        });
        
        // Сенсорные события для мобильных устройств
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (this.gameRunning && !this.gamePaused) {
                this.jump();
            }
        });
        
        // Улучшенное управление для мобильных устройств
        this.setupMobileControls();
    }
    
    startGame() {
        this.gameRunning = true;
        this.gamePaused = false;
        this.score = 0;
        this.gameSpeed = 5;
        this.obstacles = [];
        this.particles = [];
        this.crashAnimation.active = false;
        this.crashAnimation.wasStarted = false;
        this.player.y = this.groundY - 40;
        this.player.velocityY = 0;
        this.player.isJumping = false;
        this.player.justLanded = false;
        this.player.landingCooldown = 0;
        this.player.jumpAngle = 0;
        this.player.jumpScale = 1;
        this.backgroundX = 0;
        
        document.getElementById('startButton').style.display = 'none';
        document.getElementById('pauseButton').style.display = 'inline-block';
        document.getElementById('gameOver').style.display = 'none';
        
        this.gameLoop();
    }
    
    togglePause() {
        this.gamePaused = !this.gamePaused;
        if (!this.gamePaused) {
            this.gameLoop();
        }
    }
    
    restartGame() {
        this.gameRunning = false;
        this.gamePaused = false;
        document.getElementById('startButton').style.display = 'inline-block';
        document.getElementById('pauseButton').style.display = 'none';
        document.getElementById('gameOver').style.display = 'none';
        this.draw();
    }
    
    jump() {
        // Защита от повторных нажатий во время прыжка
        if (this.player.isJumping || this.crashAnimation.active) {
            return; // Игнорируем нажатия во время прыжка или анимации
        }
        
        this.player.velocityY = this.jumpPower;
        this.player.isJumping = true;
        this.createJumpParticles();
        this.sounds.jump(); // Звук прыжка
    }
    
    createJumpParticles() {
        // Создаем частицы при прыжке
        for (let i = 0; i < 8; i++) {
            this.particles.push({
                x: this.player.x + this.player.width / 2,
                y: this.player.y + this.player.height,
                velocityX: (Math.random() - 0.5) * 4,
                velocityY: Math.random() * 3 + 1,
                life: 30,
                maxLife: 30,
                size: Math.random() * 3 + 1
            });
        }
    }
    
    createLandingParticles() {
        // Создаем частицы при приземлении
        for (let i = 0; i < 12; i++) {
            this.particles.push({
                x: this.player.x + this.player.width / 2 + (Math.random() - 0.5) * 40,
                y: this.player.y + this.player.height,
                velocityX: (Math.random() - 0.5) * 6,
                velocityY: Math.random() * 4 + 2,
                life: 40,
                maxLife: 40,
                size: Math.random() * 4 + 2
            });
        }
    }
    
    updateParticles() {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const particle = this.particles[i];
            particle.x += particle.velocityX;
            particle.y += particle.velocityY;
            particle.velocityY += 0.2; // Гравитация для частиц
            particle.life--;
            
            if (particle.life <= 0) {
                this.particles.splice(i, 1);
            }
        }
    }
    
    drawParticles() {
        for (const particle of this.particles) {
            const alpha = particle.life / particle.maxLife;
            this.ctx.fillStyle = `rgba(0, 255, 65, ${alpha})`;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    updatePlayer() {
        // Гравитация
        this.player.velocityY += this.gravity;
        this.player.y += this.player.velocityY;
        
        // Анимация прыжка
        if (this.player.isJumping) {
            // Наклон при прыжке
            this.player.jumpAngle = Math.sin(this.player.velocityY * 0.1) * 0.3;
            // Сжатие при прыжке
            this.player.jumpScale = 1 + Math.abs(this.player.velocityY) * 0.01;
        } else {
            // Плавный возврат к нормальному состоянию
            this.player.jumpAngle *= 0.9;
            this.player.jumpScale = 1 + (this.player.jumpScale - 1) * 0.9;
        }
        
        // Приземление
        if (this.player.y >= this.groundY - 40) {
            this.player.y = this.groundY - 40;
            this.player.velocityY = 0;
            if (this.player.isJumping) {
                this.player.justLanded = true;
                this.player.landingCooldown = 10; // 10 кадров защиты
                this.createLandingParticles();
                this.sounds.land(); // Звук приземления
            }
            this.player.isJumping = false;
        }
        
        // Обработка кулдауна приземления
        if (this.player.landingCooldown > 0) {
            this.player.landingCooldown--;
        } else {
            this.player.justLanded = false;
        }
        
        // Анимация скейта
        this.player.skateOffset = Math.sin(Date.now() * 0.01) * 2;
    }
    
    spawnObstacle() {
        // Очень редкое появление препятствий для простой игры
        if (Math.random() < 0.002) {
            const type = this.obstacleTypes[Math.floor(Math.random() * this.obstacleTypes.length)];
            this.obstacles.push({
                x: this.gameWidth,
                y: type.y,
                width: type.width,
                height: type.height,
                type: type.name
            });
        }
    }
    

    
    updateObstacles() {
        for (let i = this.obstacles.length - 1; i >= 0; i--) {
            const obstacle = this.obstacles[i];
            obstacle.x -= this.gameSpeed;
            
            if (obstacle.x + obstacle.width < 0) {
                this.obstacles.splice(i, 1);
            }
        }
    }
    

    
    checkCollisions() {
        // Игнорируем столкновения если уже идет анимация рассыпания
        if (this.crashAnimation.active) {
            return;
        }
        
        // НОВАЯ ЛОГИКА: Проверяем столкновение с более точными хитбоксами
        for (const obstacle of this.obstacles) {
            // Хитбокс игрока (собака + скейт)
            const playerLeft = this.player.x + 10;  // Учитываем отступы собаки
            const playerRight = this.player.x + 50; // Учитываем ширину собаки
            const playerTop = this.player.y + 5;    // Учитываем отступы собаки
            const playerBottom = this.player.y + 35; // Учитываем высоту собаки
            
            // Хитбокс препятствия
            const obstacleLeft = obstacle.x;
            const obstacleRight = obstacle.x + obstacle.width;
            const obstacleTop = obstacle.y;
            const obstacleBottom = obstacle.y + obstacle.height;
            
            // Проверяем пересечение
            const horizontalOverlap = playerLeft < obstacleRight && playerRight > obstacleLeft;
            const verticalOverlap = playerTop < obstacleBottom && playerBottom > obstacleTop;
            
            if (horizontalOverlap && verticalOverlap) {
                this.startCrashAnimation();
                return;
            }
        }
    }
    
    startCrashAnimation() {
        console.log('🎬 ЗАПУСКАЕМ АНИМАЦИЮ РАССЫПАНИЯ!');
        this.crashAnimation.active = true;
        this.crashAnimation.wasStarted = true;  // Устанавливаем флаг
        this.sounds.crash(); // Звук столкновения
        this.crashAnimation.time = 0;
        this.crashAnimation.pieces = [];
        
        // Создаем кусочки собаки
        const centerX = this.player.x + this.player.width / 2;
        const centerY = this.player.y + this.player.height / 2;
        
        // Голова
        this.crashAnimation.pieces.push({
            x: centerX - 10,
            y: centerY - 15,
            width: 20,
            height: 15,
            velocityX: (Math.random() - 0.5) * 8,
            velocityY: -Math.random() * 6 - 2,
            rotation: 0,
            rotationSpeed: (Math.random() - 0.5) * 0.3,
            color: '#00ff41'
        });
        
        // Тело
        this.crashAnimation.pieces.push({
            x: centerX - 15,
            y: centerY - 5,
            width: 30,
            height: 20,
            velocityX: (Math.random() - 0.5) * 6,
            velocityY: -Math.random() * 4 - 1,
            rotation: 0,
            rotationSpeed: (Math.random() - 0.5) * 0.2,
            color: '#00ff41'
        });
        
        // Лапы
        for (let i = 0; i < 4; i++) {
            this.crashAnimation.pieces.push({
                x: centerX - 5 + (i % 2) * 10,
                y: centerY + 5 + Math.floor(i / 2) * 10,
                width: 8,
                height: 8,
                velocityX: (Math.random() - 0.5) * 10,
                velocityY: -Math.random() * 8 - 1,
                rotation: 0,
                rotationSpeed: (Math.random() - 0.5) * 0.4,
                color: '#000'
            });
        }
        
        // Скейт
        this.crashAnimation.pieces.push({
            x: centerX - 20,
            y: centerY + 15,
            width: 40,
            height: 6,
            velocityX: (Math.random() - 0.5) * 4,
            velocityY: -Math.random() * 3,
            rotation: 0,
            rotationSpeed: (Math.random() - 0.5) * 0.1,
            color: '#00ff41'
        });
    }
    
    updateCrashAnimation() {
        if (!this.crashAnimation.active) return;
        
        this.crashAnimation.time++;
        
        // Обновляем кусочки
        for (const piece of this.crashAnimation.pieces) {
            piece.x += piece.velocityX;
            piece.y += piece.velocityY;
            piece.velocityY += 0.3; // Гравитация
            piece.rotation += piece.rotationSpeed;
        }
        
        // Заканчиваем анимацию
        if (this.crashAnimation.time >= this.crashAnimation.maxTime) {
            this.crashAnimation.active = false;
            this.gameOver();
        }
    }
    
    drawCrashAnimation() {
        if (!this.crashAnimation.active) return;
        
        for (const piece of this.crashAnimation.pieces) {
            this.ctx.save();
            this.ctx.translate(piece.x + piece.width / 2, piece.y + piece.height / 2);
            this.ctx.rotate(piece.rotation);
            this.ctx.fillStyle = piece.color;
            this.ctx.fillRect(-piece.width / 2, -piece.height / 2, piece.width, piece.height);
            this.ctx.restore();
        }
    }
    
    gameOver() {
        // Игра заканчивается ТОЛЬКО после анимации рассыпания
        if (!this.crashAnimation.wasStarted) {
            console.log('❌ Игнорируем gameOver() - анимация не была запущена!');
            return;
        }
        
        console.log('✅ Игра заканчивается ПОСЛЕ анимации рассыпания!');
        
        this.gameRunning = false;
        this.gamePaused = false;
        
        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('dogSkateHighScore', this.highScore);
            this.highScoreElement.textContent = this.highScore;
        }
        
        this.finalScoreElement.textContent = this.score;
        document.getElementById('gameOver').style.display = 'block';
        document.getElementById('pauseButton').style.display = 'none';
        
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        // Вызываем Telegram обработчик если он есть
        if (this.onGameOver && typeof this.onGameOver === 'function') {
            this.onGameOver();
        }
    }
    
    drawBackground() {
        // Эффект размытия при высокой скорости
        const blurAmount = Math.min(this.gameSpeed * 0.5, 10);
        this.ctx.filter = `blur(${blurAmount}px)`;
        
        // Градиентное небо
        const gradient = this.ctx.createLinearGradient(0, 0, 0, this.gameHeight);
        gradient.addColorStop(0, '#0a0a0a');
        gradient.addColorStop(1, '#1a1a1a');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.gameWidth, this.gameHeight);
        
        // Звезды с эффектом скорости
        this.ctx.fillStyle = '#00ff41';
        for (let i = 0; i < 50; i++) {
            const x = (i * 37) % this.gameWidth;
            const y = (i * 73) % (this.gameHeight - 100);
            const size = 1 + (this.gameSpeed * 0.1);
            this.ctx.fillRect(x, y, size, size);
        }
        
        // Земля
        this.ctx.fillStyle = '#00ff41';
        this.ctx.fillRect(0, this.groundY, this.gameWidth, this.gameHeight - this.groundY);
        
        // Дорожная разметка с эффектом скорости
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 3 + (this.gameSpeed * 0.2);
        this.ctx.setLineDash([20, 20]);
        this.ctx.lineDashOffset = this.backgroundX;
        this.ctx.beginPath();
        this.ctx.moveTo(0, this.groundY + 10);
        this.ctx.lineTo(this.gameWidth, this.groundY + 10);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Сброс фильтра
        this.ctx.filter = 'none';
    }
    
    drawPlayer() {
        // Сохраняем текущее состояние canvas
        this.ctx.save();
        
        // Применяем трансформации для анимации прыжка
        const centerX = this.player.x + this.player.width / 2;
        const centerY = this.player.y + this.player.height / 2;
        
        this.ctx.translate(centerX, centerY);
        this.ctx.rotate(this.player.jumpAngle);
        this.ctx.scale(this.player.jumpScale, 1);
        this.ctx.translate(-centerX, -centerY);
        
        this.drawStylishSkate();
        this.drawStylishDog();
        
        // Восстанавливаем состояние canvas
        this.ctx.restore();
    }
    
    drawStylishSkate() {
        const skateX = this.player.x - 10;
        const skateY = this.player.y + 35;
        
        // Основная доска скейта
        this.ctx.fillStyle = '#00ff41';
        this.ctx.fillRect(skateX, skateY, 80, 8);
        
        // Неоновое свечение доски
        this.ctx.shadowColor = '#00ff41';
        this.ctx.shadowBlur = 3;
        this.ctx.strokeStyle = '#00ff41';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(skateX, skateY, 80, 8);
        this.ctx.shadowBlur = 0;
        
        // Колеса
        this.ctx.fillStyle = '#000';
        this.ctx.beginPath();
        this.ctx.arc(skateX - 5, skateY + 4, 8, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.arc(skateX + 85, skateY + 4, 8, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Детали колес
        this.ctx.strokeStyle = '#00ff41';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(skateX - 5, skateY + 4, 4, 0, Math.PI * 2);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.arc(skateX + 85, skateY + 4, 4, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Подвески
        this.ctx.fillStyle = '#00ff41';
        this.ctx.fillRect(skateX - 2, skateY - 2, 4, 12);
        this.ctx.fillRect(skateX + 78, skateY - 2, 4, 12);
    }
    
    drawStylishDog() {
        const dogX = this.player.x;
        const dogY = this.player.y;
        
        // Тело собаки (более округлое)
        this.ctx.fillStyle = '#00ff41';
        this.ctx.beginPath();
        this.ctx.roundRect(dogX + 10, dogY + 5, 40, 30, 8);
        this.ctx.fill();
        
        // Голова (более округлая)
        this.ctx.beginPath();
        this.ctx.roundRect(dogX + 45, dogY, 25, 20, 10);
        this.ctx.fill();
        
        // Уши (треугольные)
        this.ctx.fillStyle = '#000';
        this.ctx.beginPath();
        this.ctx.moveTo(dogX + 47, dogY - 5);
        this.ctx.lineTo(dogX + 51, dogY - 8);
        this.ctx.lineTo(dogX + 55, dogY - 5);
        this.ctx.closePath();
        this.ctx.fill();
        
        this.ctx.beginPath();
        this.ctx.moveTo(dogX + 57, dogY - 5);
        this.ctx.lineTo(dogX + 61, dogY - 8);
        this.ctx.lineTo(dogX + 65, dogY - 5);
        this.ctx.closePath();
        this.ctx.fill();
        
        // Глаза с бликами
        this.ctx.fillStyle = '#000';
        this.ctx.beginPath();
        this.ctx.arc(dogX + 52, dogY + 6, 3, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.arc(dogX + 60, dogY + 6, 3, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Блики в глазах
        this.ctx.fillStyle = '#00ff41';
        this.ctx.beginPath();
        this.ctx.arc(dogX + 51, dogY + 5, 1, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.arc(dogX + 59, dogY + 5, 1, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Нос
        this.ctx.fillStyle = '#000';
        this.ctx.beginPath();
        this.ctx.arc(dogX + 65, dogY + 9, 2, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Лапы (более детальные)
        this.ctx.fillStyle = '#000';
        this.ctx.beginPath();
        this.ctx.roundRect(dogX + 15, dogY + 30, 8, 10, 4);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.roundRect(dogX + 35, dogY + 30, 8, 10, 4);
        this.ctx.fill();
        
        // Хвост (изогнутый)
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 4;
        this.ctx.lineCap = 'round';
        this.ctx.beginPath();
        this.ctx.moveTo(dogX, dogY + 12);
        this.ctx.quadraticCurveTo(dogX - 10, dogY + 8, dogX - 15, dogY + 12);
        this.ctx.stroke();
        
        // Неоновое свечение собаки
        this.ctx.shadowColor = '#00ff41';
        this.ctx.shadowBlur = 2;
        this.ctx.strokeStyle = '#00ff41';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.roundRect(dogX + 10, dogY + 5, 40, 30, 8);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.roundRect(dogX + 45, dogY, 25, 20, 10);
        this.ctx.stroke();
        this.ctx.shadowBlur = 0;
    }
    
    drawObstacles() {
        for (const obstacle of this.obstacles) {
            this.drawStylishBarrier(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        }
    }
    
    drawStylishBarrier(x, y, width, height) {
        this.drawNeonBarrier(x, y, width, height);
    }
    
    drawNeonBarrier(x, y, width, height) {
        // Стильный неоновый барьер в черно-зеленой гамме
        
        // Основная стойка
        this.ctx.fillStyle = '#00ff41';
        this.ctx.fillRect(x + width * 0.3, y, width * 0.4, height);
        
        // Неоновое свечение
        this.ctx.shadowColor = '#00ff41';
        this.ctx.shadowBlur = 8;
        this.ctx.strokeStyle = '#00ff41';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(x + width * 0.3, y, width * 0.4, height);
        this.ctx.shadowBlur = 0;
        
        // Верхняя перекладина
        this.ctx.fillStyle = '#00ff41';
        this.ctx.fillRect(x, y + height * 0.2, width, height * 0.1);
        this.ctx.fillRect(x, y + height * 0.6, width, height * 0.1);
        
        // Неоновые полосы на перекладинах
        this.ctx.shadowColor = '#00ff41';
        this.ctx.shadowBlur = 4;
        this.ctx.strokeStyle = '#00ff41';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x, y + height * 0.2, width, height * 0.1);
        this.ctx.strokeRect(x, y + height * 0.6, width, height * 0.1);
        this.ctx.shadowBlur = 0;
        
        // Центральная неоновая линия
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.moveTo(x + width * 0.5, y + height * 0.1);
        this.ctx.lineTo(x + width * 0.5, y + height * 0.9);
        this.ctx.stroke();
        
        // Боковые акценты
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(x + width * 0.1, y + height * 0.3, width * 0.1, height * 0.4);
        this.ctx.fillRect(x + width * 0.8, y + height * 0.3, width * 0.1, height * 0.4);
    }
    

    
    draw() {
        this.drawBackground();
        this.drawParticles();
        
        // Рисуем игрока только если нет анимации столкновения
        if (!this.crashAnimation.active) {
            this.drawPlayer();
        } else {
            this.drawCrashAnimation();
        }
        
        this.drawObstacles();
    }
    

    

    
    gameLoop(currentTime = 0) {
        if (!this.gameRunning || this.gamePaused) return;
        
        const deltaTime = currentTime - this.lastTime;
        this.lastTime = currentTime;
        
        // Обновление
        this.updatePlayer();
        this.updateParticles();
        this.updateCrashAnimation();
        
        // Если НЕ идет анимация рассыпания, продолжаем игру
        if (!this.crashAnimation.active) {
            this.spawnObstacle();
            this.updateObstacles();
            this.checkCollisions();
            
            // Увеличение скорости
            this.gameSpeed += this.speedIncrease;
            
            // Обновление счета
            this.score += 1;
            this.scoreElement.textContent = this.score;
        }
        
        // Обновление фона (всегда)
        this.backgroundX += this.gameSpeed * 0.5;
        
        // Отрисовка
        this.draw();
        
        this.animationId = requestAnimationFrame((time) => this.gameLoop(time));
    }
}

// Инициализация игры
document.addEventListener('DOMContentLoaded', () => {
    new DogSkateGame();
});
