"""
Скрипт для тестирования функциональности смены пароля
"""
import requests
import json

# Конфигурация
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/accounts/token/"
CHANGE_PASSWORD_URL = f"{BASE_URL}/accounts/change-password/"

def login(username, password):
    """Вход в систему и получение токена"""
    print(f"\n🔐 Попытка входа для пользователя: {username}")
    
    response = requests.post(LOGIN_URL, json={
        "username": username,
        "password": password
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access')
        print(f"✅ Вход успешен! Токен получен.")
        return token
    else:
        print(f"❌ Ошибка входа: {response.status_code}")
        print(f"Ответ: {response.text}")
        return None

def change_password(token, old_password, new_password, confirm_password):
    """Смена пароля"""
    print(f"\n🔄 Попытка смены пароля...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "old_password": old_password,
        "new_password": new_password,
        "confirm_password": confirm_password
    }
    
    response = requests.post(CHANGE_PASSWORD_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Пароль успешно изменен!")
        print(f"Сообщение: {result.get('message')}")
        print(f"Детали: {result.get('detail')}")
        return True
    else:
        print(f"❌ Ошибка смены пароля: {response.status_code}")
        print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return False

def test_scenarios():
    """Тестирование различных сценариев"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СМЕНЫ ПАРОЛЯ")
    print("=" * 60)
    
    # ВАЖНО: Замените эти данные на реальные тестовые данные
    TEST_USERNAME = "test_student"  # Замените на реального пользователя
    TEST_OLD_PASSWORD = "test123"   # Текущий пароль
    TEST_NEW_PASSWORD = "NewPass123!"  # Новый пароль
    
    print(f"\n📋 Конфигурация теста:")
    print(f"   Username: {TEST_USERNAME}")
    print(f"   Backend URL: {BASE_URL}")
    
    # Шаг 1: Вход в систему
    token = login(TEST_USERNAME, TEST_OLD_PASSWORD)
    if not token:
        print("\n❌ Не удалось войти в систему. Проверьте учетные данные.")
        return
    
    # Шаг 2: Успешная смена пароля
    print("\n" + "=" * 60)
    print("ТЕСТ 1: Успешная смена пароля")
    print("=" * 60)
    success = change_password(token, TEST_OLD_PASSWORD, TEST_NEW_PASSWORD, TEST_NEW_PASSWORD)
    
    if success:
        # Шаг 3: Попытка входа со старым паролем (должна провалиться)
        print("\n" + "=" * 60)
        print("ТЕСТ 2: Вход со старым паролем (должен провалиться)")
        print("=" * 60)
        old_token = login(TEST_USERNAME, TEST_OLD_PASSWORD)
        if not old_token:
            print("✅ Правильно! Старый пароль больше не работает.")
        else:
            print("❌ ОШИБКА: Старый пароль все еще работает!")
        
        # Шаг 4: Вход с новым паролем
        print("\n" + "=" * 60)
        print("ТЕСТ 3: Вход с новым паролем")
        print("=" * 60)
        new_token = login(TEST_USERNAME, TEST_NEW_PASSWORD)
        if new_token:
            print("✅ Отлично! Новый пароль работает.")
            
            # Возвращаем старый пароль обратно для последующих тестов
            print("\n🔄 Возвращаем старый пароль...")
            change_password(new_token, TEST_NEW_PASSWORD, TEST_OLD_PASSWORD, TEST_OLD_PASSWORD)
        else:
            print("❌ ОШИБКА: Не удалось войти с новым паролем!")
    
    # Тест 5: Неправильный старый пароль
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Неправильный старый пароль")
    print("=" * 60)
    token = login(TEST_USERNAME, TEST_OLD_PASSWORD)
    if token:
        change_password(token, "wrong_password", "NewPass123!", "NewPass123!")
    
    # Тест 6: Несовпадающие новые пароли
    print("\n" + "=" * 60)
    print("ТЕСТ 5: Несовпадающие новые пароли")
    print("=" * 60)
    token = login(TEST_USERNAME, TEST_OLD_PASSWORD)
    if token:
        change_password(token, TEST_OLD_PASSWORD, "NewPass123!", "DifferentPass123!")
    
    # Тест 7: Слабый пароль
    print("\n" + "=" * 60)
    print("ТЕСТ 6: Слабый пароль (слишком короткий)")
    print("=" * 60)
    token = login(TEST_USERNAME, TEST_OLD_PASSWORD)
    if token:
        change_password(token, TEST_OLD_PASSWORD, "123", "123")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║         ТЕСТ ФУНКЦИОНАЛЬНОСТИ СМЕНЫ ПАРОЛЯ                ║
╚═══════════════════════════════════════════════════════════╝

ВНИМАНИЕ! Перед запуском:
1. Убедитесь, что Django сервер запущен (python manage.py runserver)
2. Измените TEST_USERNAME и TEST_OLD_PASSWORD на реальные данные
3. Убедитесь, что тестовый пользователь существует в базе данных

Нажмите Enter для продолжения или Ctrl+C для отмены...
    """)
    
    try:
        input()
        test_scenarios()
    except KeyboardInterrupt:
        print("\n\n❌ Тестирование отменено пользователем.")
    except Exception as e:
        print(f"\n\n❌ Произошла ошибка: {e}")
