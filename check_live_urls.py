#!/usr/bin/env python
"""
Проверка текущего состояния URL routing в ЗАПУЩЕННОМ сервере
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, '/Users/adminbaike/Desktop/projects/SkyLearn')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.urls import get_resolver
from result.urls import router
from result.views import LecturerBulkGradesViewSet

print("=" * 80)
print("ПРОВЕРКА URL ROUTING В ТЕКУЩЕМ ПРОЦЕССЕ")
print("=" * 80)

# Проверяем ViewSet
print("\n1️⃣ Проверка ViewSet класса:")
print(f"   ViewSet: {LecturerBulkGradesViewSet}")
print(f"   Метод bulk_update существует: {hasattr(LecturerBulkGradesViewSet, 'bulk_update')}")

if hasattr(LecturerBulkGradesViewSet, 'bulk_update'):
    method = getattr(LecturerBulkGradesViewSet, 'bulk_update')
    print(f"   detail: {getattr(method, 'detail', 'N/A')}")
    print(f"   methods: {getattr(method, 'mapping', 'N/A')}")
    print(f"   url_path: {getattr(method, 'url_path', 'НЕ УСТАНОВЛЕН ❌')}")
    print(f"   url_name: {getattr(method, 'url_name', 'N/A')}")

# Проверяем Router
print("\n2️⃣ Проверка Router:")
print(f"   Registered viewsets: {len(router.registry)}")
for prefix, viewset, basename in router.registry:
    if 'bulk' in prefix.lower():
        print(f"   ✅ Найден: {prefix} -> {viewset.__name__} (basename: {basename})")

# Проверяем URL resolution
print("\n3️⃣ Проверка URL Resolution:")
resolver = get_resolver()

test_urls = [
    '/result/api/lecturer/bulk-grades/bulk-update/',
    '/result/api/lecturer/bulk-grades/bulk_update/',
]

for url in test_urls:
    try:
        match = resolver.resolve(url)
        print(f"   ✅ {url}")
        print(f"      View: {match.func.cls.__name__}")
        print(f"      Actions: {match.func.actions}")
    except Exception as e:
        print(f"   ❌ {url}")
        print(f"      Ошибка: Не найден")

# Проверяем reverse
print("\n4️⃣ Проверка reverse():")
from django.urls import reverse, NoReverseMatch

try:
    url = reverse('lecturer-bulk-grades-bulk-update')
    print(f"   ✅ reverse('lecturer-bulk-grades-bulk-update') = {url}")
except NoReverseMatch as e:
    print(f"   ❌ reverse('lecturer-bulk-grades-bulk-update') не найден")

print("\n" + "=" * 80)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 80)
