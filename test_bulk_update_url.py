#!/usr/bin/env python
"""
Тест для проверки доступности endpoint bulk-update
"""
import os
import django
import sys

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver

def test_url_exists():
    """Проверяем что URL bulk-update существует"""
    resolver = get_resolver()
    
    # Тестируем URL с дефисами (правильный)
    url_with_dashes = '/result/api/lecturer/bulk-grades/bulk-update/'
    
    print("🔍 Проверяем URL с дефисами (bulk-update)...")
    try:
        match = resolver.resolve(url_with_dashes)
        print(f"✅ URL найден: {url_with_dashes}")
        print(f"   View: {match.func.__name__}")
        print(f"   View class: {match.func.cls.__name__}")
        print(f"   Actions: {match.func.actions}")
        return True
    except Exception as e:
        print(f"❌ URL не найден: {url_with_dashes}")
        print(f"   Ошибка: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("ТЕСТ ДОСТУПНОСТИ ENDPOINT")
    print("=" * 60)
    
    success = test_url_exists()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН: Endpoint доступен!")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН: Endpoint недоступен!")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
