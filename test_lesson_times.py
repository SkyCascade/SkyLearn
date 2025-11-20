#!/usr/bin/env python
"""
Тест функциональности LessonTime и обновленного ScheduleItem
"""

import os
import sys
import django
from datetime import date, time

# Настройка Django окружения
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Group
from course.models import Program, Course
from attendance.models import LessonTime, ScheduleItem

User = get_user_model()


def test_lesson_times():
    """Тестирование LessonTime и ScheduleItem с датами"""
    
    print("=" * 80)
    print("ТЕСТ LESSON TIME И SCHEDULE ITEM")
    print("=" * 80)
    
    # Очистка старых данных
    print("\n0. Очистка старых тестовых данных...")
    User.objects.filter(username='test_admin').delete()
    print("✓ Старые данные удалены")
    
    # 1. Создаем администратора
    print("\n1. Создание администратора...")
    admin = User.objects.create_user(
        username='test_admin',
        email='test_admin@test.com',
        password='test123',
        is_superuser=True,
        is_staff=True,
        first_name='Test',
        last_name='Admin'
    )
    print(f"✓ Создан admin: {admin.username}")
    
    # 2. Создаем времена уроков
    print("\n2. Создание времен уроков...")
    
    lesson1 = LessonTime.objects.create(
        order=1,
        start_time=time(9, 0),
        end_time=time(10, 30),
        admin=admin
    )
    print(f"✓ {lesson1}")
    
    lesson2 = LessonTime.objects.create(
        order=2,
        start_time=time(10, 40),
        end_time=time(12, 10),
        admin=admin
    )
    print(f"✓ {lesson2}")
    
    lesson3 = LessonTime.objects.create(
        order=3,
        start_time=time(12, 40),
        end_time=time(14, 10),
        admin=admin
    )
    print(f"✓ {lesson3}")
    
    lesson4 = LessonTime.objects.create(
        order=4,
        start_time=time(14, 20),
        end_time=time(15, 50),
        admin=admin
    )
    print(f"✓ {lesson4}")
    
    # 3. Создаем необходимые данные для расписания
    print("\n3. Создание программы, курса и группы...")
    
    program = Program.objects.create(
        title='Computer Science',
        summary='CS Program',
        admin=admin
    )
    print(f"✓ Программа: {program.title}")
    
    course = Course.objects.create(
        title='Python Programming',
        code='CS101',
        credit=3,
        program=program,
        level='100',
        year='1',
        semester='First',
        admin=admin
    )
    print(f"✓ Курс: {course.title}")
    
    group = Group.objects.create(
        name='CS-101',
        admin=admin
    )
    print(f"✓ Группа: {group.name}")
    
    # 4. Создаем расписание с использованием LessonTime
    print("\n4. Создание расписания...")
    
    schedule1 = ScheduleItem.objects.create(
        course=course,
        group=group,
        lesson_time=lesson1,
        day='Monday',
        date=date(2025, 11, 25),
        admin=admin
    )
    print(f"✓ Расписание создано: {schedule1}")
    print(f"  - Время начала: {schedule1.start_time}")
    print(f"  - Время окончания: {schedule1.end_time}")
    print(f"  - Номер урока: {schedule1.lesson_order}")
    
    schedule2 = ScheduleItem.objects.create(
        course=course,
        group=group,
        lesson_time=lesson3,
        day='Wednesday',
        date=date(2025, 11, 27),
        admin=admin
    )
    print(f"✓ Расписание создано: {schedule2}")
    print(f"  - Время начала: {schedule2.start_time}")
    print(f"  - Время окончания: {schedule2.end_time}")
    print(f"  - Номер урока: {schedule2.lesson_order}")
    
    # 5. Проверяем автоматическое определение времени
    print("\n5. Проверка автоматического определения времени...")
    
    all_schedules = ScheduleItem.objects.filter(admin=admin).order_by('date', 'lesson_time__order')
    print(f"Найдено расписаний: {all_schedules.count()}")
    
    for schedule in all_schedules:
        print(f"\n  {schedule.day}, {schedule.date}")
        print(f"  Курс: {schedule.course.title}")
        print(f"  Урок #{schedule.lesson_order}: {schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}")
    
    # 6. Проверяем фильтрацию по админу
    print("\n6. Проверка фильтрации по админу...")
    
    admin_lesson_times = LessonTime.objects.filter(admin=admin)
    print(f"Времена уроков admin: {admin_lesson_times.count()} (ожидается 4)")
    assert admin_lesson_times.count() == 4, "Должно быть 4 времени урока"
    
    admin_schedules = ScheduleItem.objects.filter(admin=admin)
    print(f"Расписания admin: {admin_schedules.count()} (ожидается 2)")
    assert admin_schedules.count() == 2, "Должно быть 2 расписания"
    
    # 7. Очистка
    print("\n7. Очистка тестовых данных...")
    admin.delete()
    print("✓ Тестовые данные удалены")
    
    print("\n" + "=" * 80)
    print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 80)


if __name__ == '__main__':
    test_lesson_times()
