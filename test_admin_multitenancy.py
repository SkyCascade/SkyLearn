#!/usr/bin/env python
"""
Тест мультитенантности на уровне администраторов
Проверяет, что каждый администратор видит только свои данные
"""

import os
import sys
import django

# Настройка Django окружения
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Student, Group
from course.models import Program, Course
from core.models import Semester, NewsAndEvents

User = get_user_model()


def test_multitenancy():
    """Тестирование мультитенантности"""
    
    print("=" * 80)
    print("ТЕСТ МУЛЬТИТЕНАНТНОСТИ НА УРОВНЕ АДМИНИСТРАТОРОВ")
    print("=" * 80)
    
    # Очищаем старые тестовые данные, если они есть
    print("\n0. Очистка старых тестовых данных...")
    User.objects.filter(username__in=['admin1', 'admin2']).delete()
    print("✓ Старые тестовые данные удалены")
    
    # 1. Создаем двух админов
    print("\n1. Создание двух администраторов...")
    admin1 = User.objects.create_user(
        username='admin1',
        email='admin1@test.com',
        password='test123',
        is_superuser=True,
        is_staff=True,
        first_name='Admin',
        last_name='One'
    )
    print(f"✓ Создан admin1: {admin1.username}")
    
    admin2 = User.objects.create_user(
        username='admin2',
        email='admin2@test.com',
        password='test123',
        is_superuser=True,
        is_staff=True,
        first_name='Admin',
        last_name='Two'
    )
    print(f"✓ Создан admin2: {admin2.username}")
    
    # 2. Создаем данные для admin1
    print("\n2. Создание данных для admin1...")
    
    # Программа
    program1 = Program.objects.create(
        title='Computer Science Admin1',
        summary='CS program for admin1',
        admin=admin1
    )
    print(f"✓ Создана программа для admin1: {program1.title}")
    
    # Группа
    group1 = Group.objects.create(
        name='CS-101 Admin1',
        admin=admin1
    )
    print(f"✓ Создана группа для admin1: {group1.name}")
    
    # Семестр
    semester1 = Semester.objects.create(
        semester='First',
        is_current_semester=True,
        admin=admin1
    )
    print(f"✓ Создан семестр для admin1: {semester1.semester}")
    
    # Курс
    course1 = Course.objects.create(
        title='Python Programming Admin1',
        code='CS101',
        credit=3,
        program=program1,
        level='100',
        year='1',
        semester='First',
        admin=admin1
    )
    print(f"✓ Создан курс для admin1: {course1.title}")
    
    # Новость
    news1 = NewsAndEvents.objects.create(
        title='News from Admin1',
        summary='This is news from admin1',
        posted_as='News',
        admin=admin1
    )
    print(f"✓ Создана новость для admin1: {news1.title}")
    
    # 3. Создаем данные для admin2
    print("\n3. Создание данных для admin2...")
    
    # Программа
    program2 = Program.objects.create(
        title='Computer Science Admin2',
        summary='CS program for admin2',
        admin=admin2
    )
    print(f"✓ Создана программа для admin2: {program2.title}")
    
    # Группа
    group2 = Group.objects.create(
        name='CS-101 Admin2',
        admin=admin2
    )
    print(f"✓ Создана группа для admin2: {group2.name}")
    
    # Семестр
    semester2 = Semester.objects.create(
        semester='First',
        is_current_semester=True,
        admin=admin2
    )
    print(f"✓ Создан семестр для admin2: {semester2.semester}")
    
    # Курс
    course2 = Course.objects.create(
        title='Python Programming Admin2',
        code='CS102',
        credit=3,
        program=program2,
        level='100',
        year='1',
        semester='First',
        admin=admin2
    )
    print(f"✓ Создан курс для admin2: {course2.title}")
    
    # Новость
    news2 = NewsAndEvents.objects.create(
        title='News from Admin2',
        summary='This is news from admin2',
        posted_as='News',
        admin=admin2
    )
    print(f"✓ Создана новость для admin2: {news2.title}")
    
    # 4. Проверяем изоляцию данных
    print("\n4. Проверка изоляции данных...")
    
    # Проверка программ
    admin1_programs = Program.objects.filter(admin=admin1)
    admin2_programs = Program.objects.filter(admin=admin2)
    
    print(f"\nПрограммы admin1: {admin1_programs.count()} (ожидается 1)")
    assert admin1_programs.count() == 1, "Admin1 должен видеть только 1 программу"
    print(f"  ✓ {admin1_programs.first().title}")
    
    print(f"Программы admin2: {admin2_programs.count()} (ожидается 1)")
    assert admin2_programs.count() == 1, "Admin2 должен видеть только 1 программу"
    print(f"  ✓ {admin2_programs.first().title}")
    
    # Проверка групп
    admin1_groups = Group.objects.filter(admin=admin1)
    admin2_groups = Group.objects.filter(admin=admin2)
    
    print(f"\nГруппы admin1: {admin1_groups.count()} (ожидается 1)")
    assert admin1_groups.count() == 1, "Admin1 должен видеть только 1 группу"
    print(f"  ✓ {admin1_groups.first().name}")
    
    print(f"Группы admin2: {admin2_groups.count()} (ожидается 1)")
    assert admin2_groups.count() == 1, "Admin2 должен видеть только 1 группу"
    print(f"  ✓ {admin2_groups.first().name}")
    
    # Проверка семестров
    admin1_semesters = Semester.objects.filter(admin=admin1)
    admin2_semesters = Semester.objects.filter(admin=admin2)
    
    print(f"\nСеместры admin1: {admin1_semesters.count()} (ожидается 1)")
    assert admin1_semesters.count() == 1, "Admin1 должен видеть только 1 семестр"
    print(f"  ✓ {admin1_semesters.first().semester}")
    
    print(f"Семестры admin2: {admin2_semesters.count()} (ожидается 1)")
    assert admin2_semesters.count() == 1, "Admin2 должен видеть только 1 семестр"
    print(f"  ✓ {admin2_semesters.first().semester}")
    
    # Проверка курсов
    admin1_courses = Course.objects.filter(admin=admin1)
    admin2_courses = Course.objects.filter(admin=admin2)
    
    print(f"\nКурсы admin1: {admin1_courses.count()} (ожидается 1)")
    assert admin1_courses.count() == 1, "Admin1 должен видеть только 1 курс"
    print(f"  ✓ {admin1_courses.first().title}")
    
    print(f"Курсы admin2: {admin2_courses.count()} (ожидается 1)")
    assert admin2_courses.count() == 1, "Admin2 должен видеть только 1 курс"
    print(f"  ✓ {admin2_courses.first().title}")
    
    # Проверка новостей
    admin1_news = NewsAndEvents.objects.filter(admin=admin1)
    admin2_news = NewsAndEvents.objects.filter(admin=admin2)
    
    print(f"\nНовости admin1: {admin1_news.count()} (ожидается 1)")
    assert admin1_news.count() == 1, "Admin1 должен видеть только 1 новость"
    print(f"  ✓ {admin1_news.first().title}")
    
    print(f"Новости admin2: {admin2_news.count()} (ожидается 1)")
    assert admin2_news.count() == 1, "Admin2 должен видеть только 1 новость"
    print(f"  ✓ {admin2_news.first().title}")
    
    # 5. Очистка тестовых данных
    print("\n5. Очистка тестовых данных...")
    admin1.delete()
    admin2.delete()
    print("✓ Тестовые данные удалены")
    
    print("\n" + "=" * 80)
    print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 80)


if __name__ == '__main__':
    test_multitenancy()
