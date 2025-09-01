import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class BookingDatabase:
    def __init__(self, db_file="bookings.json"):
        self.db_file = db_file
        self.bookings = self.load_bookings()
    
    def load_bookings(self) -> Dict:
        """Загружает записи из файла"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_bookings(self):
        """Сохраняет записи в файл"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.bookings, f, ensure_ascii=False, indent=2)
    
    def add_booking(self, user_id: int, user_name: str, booking_data: Dict) -> str:
        """Добавляет новую запись"""
        booking_id = f"booking_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        booking = {
            'id': booking_id,
            'user_id': user_id,
            'user_name': user_name,
            'status': 'pending',  # pending, confirmed, rejected, completed
            'created_at': datetime.now().isoformat(),
            'confirmed_at': None,
            'rejected_at': None,
            **booking_data
        }
        
        self.bookings[booking_id] = booking
        self.save_bookings()
        return booking_id
    
    def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Получает запись по ID"""
        return self.bookings.get(booking_id)
    
    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Получает все записи пользователя"""
        return [booking for booking in self.bookings.values() if booking['user_id'] == user_id]
    
    def get_pending_bookings(self) -> List[Dict]:
        """Получает все ожидающие подтверждения записи"""
        return [booking for booking in self.bookings.values() if booking['status'] == 'pending']
    
    def confirm_booking(self, booking_id: str):
        """Подтверждает запись"""
        if booking_id in self.bookings:
            self.bookings[booking_id]['status'] = 'confirmed'
            self.bookings[booking_id]['confirmed_at'] = datetime.now().isoformat()
            self.save_bookings()
    
    def reject_booking(self, booking_id: str, reason: str = ""):
        """Отклоняет запись"""
        if booking_id in self.bookings:
            self.bookings[booking_id]['status'] = 'rejected'
            self.bookings[booking_id]['rejected_at'] = datetime.now().isoformat()
            self.bookings[booking_id]['rejection_reason'] = reason
            self.save_bookings()
    
    def complete_booking(self, booking_id: str):
        """Отмечает запись как завершенную"""
        if booking_id in self.bookings:
            self.bookings[booking_id]['status'] = 'completed'
            self.save_bookings()
    
    def get_upcoming_bookings(self, hours_ahead: int = 2) -> List[Dict]:
        """Получает предстоящие записи через указанное количество часов"""
        now = datetime.now()
        target_time = now + timedelta(hours=hours_ahead)
        
        upcoming = []
        for booking in self.bookings.values():
            if booking['status'] == 'confirmed':
                try:
                    booking_datetime = datetime.fromisoformat(booking['date'] + 'T' + booking['time'])
                    if now <= booking_datetime <= target_time:
                        upcoming.append(booking)
                except:
                    continue
        
        return upcoming
    
    def delete_old_bookings(self, days: int = 30):
        """Удаляет старые записи"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_bookings = []
        
        for booking_id, booking in self.bookings.items():
            try:
                created_at = datetime.fromisoformat(booking['created_at'])
                if created_at < cutoff_date:
                    old_bookings.append(booking_id)
            except:
                continue
        
        for booking_id in old_bookings:
            del self.bookings[booking_id]
        
        if old_bookings:
            self.save_bookings()
    
    def get_statistics(self) -> Dict:
        """Получает статистику по записям"""
        total = len(self.bookings)
        pending = len([b for b in self.bookings.values() if b['status'] == 'pending'])
        confirmed = len([b for b in self.bookings.values() if b['status'] == 'confirmed'])
        rejected = len([b for b in self.bookings.values() if b['status'] == 'rejected'])
        completed = len([b for b in self.bookings.values() if b['status'] == 'completed'])
        
        return {
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'rejected': rejected,
            'completed': completed
        }
