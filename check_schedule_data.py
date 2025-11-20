#!/usr/bin/env python
"""
Проверка данных курсов и групп для текущего администратора
"""
import os
import sys
import django

# Настройка Django
sys.path.append('/Users/adminbaike/Desktop/projects/SkyLearn')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, Group
from course.models import Course

def check_admin_data():
    print("=" * 60)
    print("ПРОВЕРКА ДАННЫХ ДЛЯ АДМИНИСТРАТОРОВ")
    print("=" * 60)
    
    # Получаем всех администраторов
    admins = User.objects.filter(is_superuser=True)
    
    if not admins.exists():
        print("\n❌ НЕТ АДМИНИСТРАТОРОВ В СИСТЕМЕ!")
        print("Создайте администратора:")
        print("  python manage.py createsuperuser")
        return
    
    print(f"\n✅ Найдено администраторов: {admins.count()}")
    
    for admin in admins:
        print("\n" + "=" * 60)
        print(f"📊 Администратор: {admin.username} (ID: {admin.id})")
        print("=" * 60)
        
        # Проверяем курсы
        courses = Course.objects.filter(admin=admin)
        print(f"\n📚 Курсы: {courses.count()}")
        if courses.exists():
            for course in courses[:5]:  # Показываем первые 5
                print(f"   - {course.code}: {course.title}")
            if courses.count() > 5:
                print(f"   ... и еще {courses.count() - 5}")
        else:
            print("   ⚠️ НЕТ КУРСОВ!")
            print("   Создайте курс через:")
            print("   - Admin panel: http://localhost:8000/admin/course/course/")
            print("   - Frontend: http://localhost:5174/admin/courses")
        
        # Проверяем группы
        groups = Group.objects.filter(admin=admin)
        print(f"\n👥 Группы: {groups.count()}")
        if groups.exists():
            for group in groups[:5]:  # Показываем первые 5
                students_count = group.students.count()
                print(f"   - {group.name} ({students_count} студентов)")
            if groups.count() > 5:
                print(f"   ... и еще {groups.count() - 5}")
        else:
            print("   ⚠️ НЕТ ГРУПП!")
            print("   Группа создается автоматически при создании студента через:")
            print("   - Frontend: http://localhost:5174/admin/create-students")
    
    print("\n" + "=" * 60)
    print("РЕКОМЕНДАЦИИ")
    print("=" * 60)
    
    # Проверяем что нужно создать
    needs_courses = any(Course.objects.filter(admin=admin).count() == 0 for admin in admins)
    needs_groups = any(Group.objects.filter(admin=admin).count() == 0 for admin in admins)
    
    if needs_courses:
        print("\n📝 Чтобы создать КУРСЫ:")
        print("   1. Войдите как администратор")
        print("   2. Перейдите: http://localhost:5174/admin/courses")
        print("   3. Создайте программу (Program)")
        print("   4. Создайте курс (Course)")
    
    if needs_groups:
        print("\n📝 Чтобы создать ГРУППЫ и СТУДЕНТОВ:")
        print("   1. Войдите как администратор")
        print("   2. Перейдите: http://localhost:5174/admin/create-students")
        print("   3. Создайте студента (группа создастся автоматически)")
    
    if not needs_courses and not needs_groups:
        print("\n✅ Все данные есть! Можно создавать расписание.")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_admin_data()
