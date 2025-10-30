# 🚀 Quick Fix: Django изменения не применяются

## ⚡ Быстрое решение (3 команды)

```bash
# 1. Убить все процессы Django
pkill -9 -f "manage.py runserver"

# 2. Очистить Python кеш
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null

# 3. Запустить сервер заново
python manage.py runserver
```

## 🔍 Диагностика

### Проверить запущенные процессы

```bash
ps aux | grep "manage.py runserver"
```

**Плохо:** Видите несколько процессов = конфликт

```
user  20157  ... python manage.py runserver  # 🔴 Старый
user  24248  ... python manage.py runserver  # 🔴 Старый
```

**Хорошо:** Один процесс с новым PID

```
user  25000  ... python manage.py runserver  # ✅ Свежий
```

### Проверить работу endpoint

```bash
curl -X POST http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/ \
  -H "Content-Type: application/json" \
  -d '{"course_id": 1, "grade_type": "1st_module", "grades": []}' \
  -w "\nStatus: %{http_code}\n"
```

**Ожидаемый результат:**

```json
{"detail":"Authentication credentials were not provided."}
Status: 401  ✅
```

**Если получаете 404** → Сервер использует старый код!

## 🔧 Полная очистка

Если быстрое решение не помогло:

```bash
# Убить все Python процессы (осторожно!)
pkill -9 python

# Полная очистка кеша
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Очистить Django кеш
python manage.py clear_cache 2>/dev/null || echo "No cache to clear"

# Перезапуск
python manage.py runserver
```

## 📋 Checklist

- [ ] Старые процессы убиты (`ps aux | grep runserver` показывает пусто)
- [ ] Python кеш очищен (нет `__pycache__` папок)
- [ ] Сервер перезапущен (новый PID в логах)
- [ ] Endpoint возвращает 401 (не 404)
- [ ] Тесты проходят (`python manage.py test result.tests.test_views -k bulk`)

## 🎯 Правильный URL

```
✅ /result/api/lecturer/bulk-grades/bulk-update/  (с дефисами)
❌ /result/api/lecturer/bulk-grades/bulk_update/  (с подчеркиваниями)
```

## 💡 Проблема решена?

Если endpoint возвращает **401** вместо **404** - значит backend работает! ✅

Теперь проблема только в аутентификации фронтенда (нужен JWT токен).
