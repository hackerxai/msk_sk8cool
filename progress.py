#!/usr/bin/env python3
"""
Система прогресса для MSK SK8COOL
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ProgressSystem:
    def __init__(self, db_file: str = "progress.json"):
        self.db_file = db_file
        self.progress_data = self._load_progress()
        
        # Уровни и их требования
        self.levels = {
            "novice": {"name": "🥉 Новичок", "min_sessions": 0, "max_sessions": 5},
            "amateur": {"name": "🥈 Любитель", "min_sessions": 6, "max_sessions": 15},
            "pro": {"name": "🥇 Профи", "min_sessions": 16, "max_sessions": 30},
            "master": {"name": "👑 Мастер", "min_sessions": 31, "max_sessions": 999}
        }
        
        # Достижения
        self.achievements = {
            "first_session": {
                "name": "🎯 Первая тренировка",
                "description": "Записался на первую тренировку!",
                "icon": "🎯",
                "condition": lambda sessions: len(sessions) >= 1
            },
            "beginner": {
                "name": "🔥 Начинающий",
                "description": "5 тренировок - ты на пути к успеху!",
                "icon": "🔥",
                "condition": lambda sessions: len(sessions) >= 5
            },
            "regular": {
                "name": "⚡ Регулярный",
                "description": "10 тренировок - ты настоящий скейтер!",
                "icon": "⚡",
                "condition": lambda sessions: len(sessions) >= 10
            },
            "champion": {
                "name": "🏆 Чемпион",
                "description": "25 тренировок - ты мастер скейтборда!",
                "icon": "🏆",
                "condition": lambda sessions: len(sessions) >= 25
            },
            "speed_progress": {
                "name": "🚀 Скоростной прогресс",
                "description": "3 тренировки за неделю - впечатляюще!",
                "icon": "🚀",
                "condition": lambda sessions: self._check_weekly_progress(sessions, 3)
            },
            "consistent": {
                "name": "📅 Постоянный",
                "description": "Тренируешься 3 недели подряд!",
                "icon": "📅",
                "condition": lambda sessions: self._check_consecutive_weeks(sessions, 3)
            }
        }

    def _load_progress(self) -> Dict:
        """Загружает данные прогресса из файла"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_progress(self):
        """Сохраняет данные прогресса в файл"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения прогресса: {e}")

    def _check_weekly_progress(self, sessions: List, required_count: int) -> bool:
        """Проверяет количество тренировок за последнюю неделю"""
        if len(sessions) < required_count:
            return False
            
        week_ago = datetime.now() - timedelta(days=7)
        recent_sessions = [
            session for session in sessions[-required_count:]
            if datetime.fromisoformat(session['date']) >= week_ago
        ]
        return len(recent_sessions) >= required_count

    def _check_consecutive_weeks(self, sessions: List, required_weeks: int) -> bool:
        """Проверяет тренировки в течение нескольких недель подряд"""
        if len(sessions) < required_weeks:
            return False
            
        # Группируем тренировки по неделям
        weeks = {}
        for session in sessions:
            session_date = datetime.fromisoformat(session['date'])
            week_start = session_date - timedelta(days=session_date.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            if week_key not in weeks:
                weeks[week_key] = []
            weeks[week_key].append(session)
        
        # Проверяем последние недели
        sorted_weeks = sorted(weeks.keys(), reverse=True)
        consecutive_weeks = 0
        
        for i, week in enumerate(sorted_weeks[:required_weeks]):
            if weeks[week]:  # Если в неделе были тренировки
                consecutive_weeks += 1
            else:
                break
                
        return consecutive_weeks >= required_weeks

    def add_session(self, user_id: int, user_name: str, username: str, 
                   park_name: str, session_date: str, session_time: str) -> Dict:
        """Добавляет новую тренировку и обновляет прогресс"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.progress_data:
            self.progress_data[user_id_str] = {
                "user_name": user_name,
                "username": username,
                "sessions": [],
                "achievements": [],
                "level": "novice",
                "total_sessions": 0,
                "first_session": None,
                "last_session": None
            }
        
        # Добавляем тренировку
        session_info = {
            "date": session_date,
            "time": session_time,
            "park": park_name,
            "timestamp": datetime.now().isoformat()
        }
        
        self.progress_data[user_id_str]["sessions"].append(session_info)
        self.progress_data[user_id_str]["total_sessions"] = len(self.progress_data[user_id_str]["sessions"])
        
        # Обновляем первую и последнюю тренировку
        if not self.progress_data[user_id_str]["first_session"]:
            self.progress_data[user_id_str]["first_session"] = session_date
        self.progress_data[user_id_str]["last_session"] = session_date
        
        # Обновляем уровень
        self._update_level(user_id_str)
        
        # Проверяем достижения
        new_achievements = self._check_achievements(user_id_str)
        
        # Сохраняем данные
        self._save_progress()
        
        return {
            "new_achievements": new_achievements,
            "current_level": self.progress_data[user_id_str]["level"],
            "total_sessions": self.progress_data[user_id_str]["total_sessions"]
        }

    def _update_level(self, user_id_str: str):
        """Обновляет уровень пользователя"""
        total_sessions = self.progress_data[user_id_str]["total_sessions"]
        
        for level_id, level_info in self.levels.items():
            if level_info["min_sessions"] <= total_sessions <= level_info["max_sessions"]:
                self.progress_data[user_id_str]["level"] = level_id
                break

    def _check_achievements(self, user_id_str: str) -> List[Dict]:
        """Проверяет и добавляет новые достижения"""
        user_data = self.progress_data[user_id_str]
        sessions = user_data["sessions"]
        current_achievements = set(user_data["achievements"])
        new_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            if (achievement_id not in current_achievements and 
                achievement["condition"](sessions)):
                
                user_data["achievements"].append(achievement_id)
                new_achievements.append({
                    "id": achievement_id,
                    "name": achievement["name"],
                    "description": achievement["description"],
                    "icon": achievement["icon"]
                })
        
        return new_achievements

    def get_user_progress(self, user_id: int) -> Optional[Dict]:
        """Получает прогресс пользователя"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.progress_data:
            return None
            
        user_data = self.progress_data[user_id_str]
        current_level = self.levels[user_data["level"]]
        
        # Следующий уровень
        next_level = None
        for level_id, level_info in self.levels.items():
            if level_info["min_sessions"] > user_data["total_sessions"]:
                next_level = level_info
                break
        
        # Прогресс до следующего уровня
        progress_to_next = 0
        if next_level:
            current_level_sessions = current_level["max_sessions"]
            next_level_sessions = next_level["min_sessions"]
            progress_to_next = min(100, (user_data["total_sessions"] - current_level_sessions) / 
                                 (next_level_sessions - current_level_sessions) * 100)
        
        # Получаем достижения
        user_achievements = []
        for achievement_id in user_data["achievements"]:
            if achievement_id in self.achievements:
                user_achievements.append(self.achievements[achievement_id])
        
        return {
            "user_name": user_data["user_name"],
            "username": user_data["username"],
            "current_level": current_level,
            "next_level": next_level,
            "progress_to_next": progress_to_next,
            "total_sessions": user_data["total_sessions"],
            "achievements": user_achievements,
            "first_session": user_data["first_session"],
            "last_session": user_data["last_session"],
            "sessions": user_data["sessions"][-5:]  # Последние 5 тренировок
        }

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Получает таблицу лидеров"""
        users = []
        
        for user_id, user_data in self.progress_data.items():
            users.append({
                "user_name": user_data["user_name"],
                "username": user_data["username"],
                "total_sessions": user_data["total_sessions"],
                "level": self.levels[user_data["level"]]["name"],
                "achievements_count": len(user_data["achievements"])
            })
        
        # Сортируем по количеству тренировок
        users.sort(key=lambda x: x["total_sessions"], reverse=True)
        return users[:limit]

    def format_progress_message(self, user_id: int) -> str:
        """Форматирует сообщение с прогрессом пользователя"""
        progress = self.get_user_progress(user_id)
        
        if not progress:
            return "🎯 У вас пока нет тренировок. Запишитесь на первую!"
        
        # Создаем прогресс-бар
        progress_bar = self._create_progress_bar(progress["progress_to_next"])
        
        message = f"""
🏂 *Ваш прогресс в MSK SK8COOL*

👤 *{progress['user_name']}* (@{progress['username']})

{progress['current_level']['name']}
{progress_bar} {progress['progress_to_next']:.0f}%

📊 *Статистика:*
• Всего тренировок: {progress['total_sessions']}
• Первая тренировка: {progress['first_session']}
• Последняя тренировка: {progress['last_session']}

🏆 *Достижения:* {len(progress['achievements'])}/{len(self.achievements)}
"""
        
        # Добавляем достижения
        if progress['achievements']:
            achievements_text = "\n".join([
                f"• {achievement['icon']} {achievement['name']}"
                for achievement in progress['achievements']
            ])
            message += f"\n{achievements_text}"
        
        # Следующий уровень
        if progress['next_level']:
            sessions_needed = progress['next_level']['min_sessions'] - progress['total_sessions']
            message += f"\n\n🎯 До {progress['next_level']['name']}: {sessions_needed} тренировок"
        
        return message

    def _create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Создает визуальный прогресс-бар"""
        filled = int(percentage / 100 * length)
        empty = length - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{bar}]"

    def format_leaderboard_message(self, limit: int = 5) -> str:
        """Форматирует сообщение с таблицей лидеров"""
        leaderboard = self.get_leaderboard(limit)
        
        if not leaderboard:
            return "🏆 Пока нет данных для таблицы лидеров"
        
        message = "🏆 *Топ скейтеров MSK SK8COOL*\n\n"
        
        for i, user in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {user['user_name']} (@{user['username']})\n"
            message += f"   {user['level']} • {user['total_sessions']} тренировок • {user['achievements_count']} достижений\n\n"
        
        return message
