#!/usr/bin/env python3
"""
Простой веб-сервер для игры "Собака на Скейте"
"""

import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class GameHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        # Обрабатываем запросы к игре
        if self.path == '/game' or self.path == '/game/':
            self.path = '/index.html'
        elif self.path.startswith('/game/'):
            # Убираем /game/ из пути
            self.path = self.path[5:]
        
        return super().do_GET()
    
    def end_headers(self):
        # Добавляем CORS заголовки для Telegram Web App
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_web_server(port=8080):
    """Запускает веб-сервер в отдельном потоке"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, GameHandler)
    
    def run_server():
        logger.info(f"🌐 Веб-сервер запущен на http://localhost:{port}")
        logger.info(f"🎮 Игра доступна по адресу: http://localhost:{port}/game")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Веб-сервер остановлен")
            httpd.shutdown()
    
    # Запускаем сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return httpd

if __name__ == "__main__":
    # Тестовый запуск сервера
    start_web_server()
    
    try:
        input("Нажмите Enter для остановки сервера...\n")
    except KeyboardInterrupt:
        pass
