#!/usr/bin/env python
"""
Создание стандартных времен уроков для администратора
"""
import os
import sys
import django

# Настройка Django
sys.path.append('/Users/adminbaike/Desktop/projects/SkyLearn')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from attendance.models import LessonTime

def create_lesson_times():
    print("=" * 60)
    print("СОЗДАНИЕ СТАНДАРТНЫХ ВРЕМЕН УРОКОВ")
    print("=" * 60)
    
    # Получаем администратора
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("\n❌ НЕТ АДМИНИСТРАТОРА!")
        return
    
    print(f"\n✅ Используем администратора: {admin.username}")
    
    # Стандартные времена уроков
    lesson_times_data = [
        {'order': 1, 'start_time': '09:00:00', 'end_time': '10:30:00'},
        {'order': 2, 'start_time': '10:40:00', 'end_time': '12:10:00'},
        {'order': 3, 'start_time': '12:20:00', 'end_time': '13:50:00'},
        {'order': 4, 'start_time': '14:00:00', 'end_time': '15:30:00'},
        {'order': 5, 'start_time': '15:40:00', 'end_time': '17:10:00'},
    ]
    
    print(f"\n⏰ Создание времен уроков:")
    for lt_data in lesson_times_data:
        lesson_time, created = LessonTime.objects.get_or_create(
            order=lt_data['order'],
            admin=admin,
            defaults={
                'start_time': lt_data['start_time'],
                'end_time': lt_data['end_time'],
            }
        )
        status = '✅ создано' if created else '📌 существует'
        print(f"   {status}: Урок {lesson_time.order} ({lesson_time.start_time.strftime('%H:%M')} - {lesson_time.end_time.strftime('%H:%M')})")
    
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"✅ Времен уроков: {LessonTime.objects.filter(admin=admin).count()}")
    
    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)
    print("\nТеперь времена уроков доступны в расписании:")
    print("1. Перейдите: http://localhost:5174/admin/schedule")
    print("2. Нажмите 'Добавить занятие'")
    print("3. В поле 'Время урока' выберите из списка")
    print("\n💡 Или посмотрите все времена:")
    print("   http://localhost:5174/admin/lesson-times")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    create_lesson_times()
