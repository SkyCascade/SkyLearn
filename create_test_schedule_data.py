#!/usr/bin/env python
"""
Создание тестовых данных для демонстрации функциональности расписания
"""
import os
import sys
import django

# Настройка Django
sys.path.append('/Users/adminbaike/Desktop/projects/SkyLearn')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, Group, Student
from course.models import Program, Course
from core.models import Semester

def create_test_data():
    print("=" * 60)
    print("СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ")
    print("=" * 60)
    
    # Получаем администратора
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("\n❌ НЕТ АДМИНИСТРАТОРА!")
        print("Создайте: python manage.py createsuperuser")
        return
    
    print(f"\n✅ Используем администратора: {admin.username}")
    
    # Создаем или получаем семестр
    semester, created = Semester.objects.get_or_create(
        semester="Fall",
        admin=admin,
        defaults={
            'is_current_semester': True
        }
    )
    print(f"\n📅 Семестр: {semester.semester} {'(создан)' if created else '(существует)'}")
    
    # Создаем программу
    program, created = Program.objects.get_or_create(
        title="Computer Science",
        admin=admin,
        defaults={
            'summary': 'Bachelor program in Computer Science'
        }
    )
    print(f"\n🎓 Программа: {program.title} {'(создана)' if created else '(существует)'}")
    
    # Создаем курсы
    courses_data = [
        {'code': 'CS101', 'title': 'Introduction to Programming', 'credit': 3},
        {'code': 'CS102', 'title': 'Data Structures', 'credit': 4},
        {'code': 'MATH101', 'title': 'Calculus I', 'credit': 4},
        {'code': 'ENG101', 'title': 'English Composition', 'credit': 3},
    ]
    
    print(f"\n📚 Создание курсов:")
    created_courses = []
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            code=course_data['code'],
            admin=admin,
            defaults={
                'title': course_data['title'],
                'credit': course_data['credit'],
                'program': program,
                'level': 100,
                'year': 1,
                'semester': semester,
            }
        )
        created_courses.append(course)
        status = '✅ создан' if created else '📌 существует'
        print(f"   {status}: {course.code} - {course.title}")
    
    # Создаем группы
    groups_data = [
        {'name': 'CS-101'},
        {'name': 'CS-102'},
        {'name': 'CS-103'},
    ]
    
    print(f"\n👥 Создание групп:")
    created_groups = []
    for group_data in groups_data:
        group, created = Group.objects.get_or_create(
            name=group_data['name'],
            admin=admin
        )
        created_groups.append(group)
        status = '✅ создана' if created else '📌 существует'
        print(f"   {status}: {group.name}")
    
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"✅ Программ: {Program.objects.filter(admin=admin).count()}")
    print(f"✅ Курсов: {Course.objects.filter(admin=admin).count()}")
    print(f"✅ Групп: {Group.objects.filter(admin=admin).count()}")
    print(f"✅ Семестров: {Semester.objects.filter(admin=admin).count()}")
    
    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)
    print("\nТеперь можно создавать расписание:")
    print("1. Перейдите: http://localhost:5174/admin/schedule")
    print("2. Нажмите 'Добавить занятие'")
    print("3. Выберите курс и группу из списка")
    print("4. Выберите время урока (или создайте в /admin/lesson-times)")
    print("\n💡 Также можно создать времена уроков:")
    print("   http://localhost:5174/admin/lesson-times")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    create_test_data()
