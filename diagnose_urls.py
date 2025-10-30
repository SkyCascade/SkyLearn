#!/usr/bin/env python
"""
Детальная диагностика URL routing
"""
import os
import django
import sys

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver
from rest_framework.routers import DefaultRouter
from result.views import LecturerBulkGradesViewSet

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_viewset_actions():
    print_section("1. Проверка ViewSet Actions")
    
    viewset = LecturerBulkGradesViewSet
    print(f"ViewSet: {viewset.__name__}")
    
    # Получаем все методы с декоратором @action
    actions = []
    for attr_name in dir(viewset):
        attr = getattr(viewset, attr_name)
        if hasattr(attr, 'mapping'):
            actions.append(attr_name)
        if hasattr(attr, 'detail'):
            print(f"  ✓ Найден action: {attr_name}")
            print(f"    - detail: {attr.detail}")
            print(f"    - methods: {attr.mapping}")
            if hasattr(attr, 'url_path'):
                print(f"    - url_path: {attr.url_path}")
            if hasattr(attr, 'url_name'):
                print(f"    - url_name: {attr.url_name}")
    
    if not actions:
        print("  ⚠️  Нет actions с декоратором @action")

def check_router_urls():
    print_section("2. Проверка Router URLs")
    
    from result.urls import router
    
    print(f"Router type: {type(router).__name__}")
    print(f"Registered viewsets: {len(router.registry)}")
    
    for prefix, viewset, basename in router.registry:
        print(f"\n  Prefix: {prefix}")
        print(f"  ViewSet: {viewset.__name__}")
        print(f"  Basename: {basename}")
    
    # Генерируем URL patterns
    urls = router.urls
    print(f"\n  Сгенерировано URL patterns: {len(urls)}")
    
    for url in urls:
        if 'bulk' in str(url.pattern):
            print(f"    ✓ {url.pattern}")

def check_url_resolution():
    print_section("3. Проверка URL Resolution")
    
    resolver = get_resolver()
    
    test_urls = [
        '/result/api/lecturer/bulk-grades/',
        '/result/api/lecturer/bulk-grades/bulk-update/',
        '/result/api/lecturer/bulk-grades/bulk_update/',
    ]
    
    for url in test_urls:
        print(f"\n  Тестируем: {url}")
        try:
            match = resolver.resolve(url)
            print(f"    ✅ НАЙДЕН")
            print(f"    View: {match.func.__name__}")
            if hasattr(match.func, 'cls'):
                print(f"    ViewSet: {match.func.cls.__name__}")
            if hasattr(match.func, 'actions'):
                print(f"    Actions: {match.func.actions}")
            print(f"    Kwargs: {match.kwargs}")
        except Exception as e:
            print(f"    ❌ НЕ НАЙДЕН: {e}")

def check_all_result_urls():
    print_section("4. Все URL с 'result'")
    
    resolver = get_resolver()
    
    def get_all_urls(urlpatterns, prefix=''):
        urls = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                urls.extend(get_all_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                urls.append(prefix + str(pattern.pattern))
        return urls
    
    all_urls = get_all_urls(resolver.url_patterns)
    result_urls = [url for url in all_urls if 'result' in url.lower()]
    
    print(f"\n  Найдено URL с 'result': {len(result_urls)}")
    for url in sorted(result_urls):
        if 'bulk' in url.lower() or 'grade' in url.lower():
            print(f"    {url}")

def check_reverse_url():
    print_section("5. Проверка reverse() для URL")
    
    from django.urls import reverse, NoReverseMatch
    
    test_names = [
        'lecturer-bulk-grades-list',
        'lecturer-bulk-grades-detail',
        'lecturer-bulk-grades-bulk-update',
        'lecturer-bulk-grades-bulk_update',
    ]
    
    for name in test_names:
        print(f"\n  reverse('{name}')")
        try:
            url = reverse(name)
            print(f"    ✅ {url}")
        except NoReverseMatch as e:
            print(f"    ❌ {e}")

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("  ДЕТАЛЬНАЯ ДИАГНОСТИКА URL ROUTING")
    print("=" * 80)
    
    check_viewset_actions()
    check_router_urls()
    check_url_resolution()
    check_all_result_urls()
    check_reverse_url()
    
    print("\n" + "=" * 80)
    print("  ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 80 + "\n")
