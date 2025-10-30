# 🎯 Шпаргалка для работы с SkyLearn

## ⚡ Быстрый старт

### Backend (Терминал 1)

```bash
cd ~/Desktop/projects/SkyLearn
source venv/bin/activate
python manage.py runserver
```

→ `http://localhost:8000`

### Frontend (Терминал 2)

```bash
cd ~/Desktop/projects/SkyLearn/skyfront
npm run dev
```

→ `http://localhost:5173`

## 🔧 Полезные команды

### Django (Backend)

```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Тесты
python manage.py test
python manage.py test result.tests.test_views -k bulk -v 2

# Shell
python manage.py shell

# Очистить кеш
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

### React (Frontend)

```bash
# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Сборка production
npm run build

# Линтинг
npm run lint

# Очистка и переустановка
rm -rf node_modules package-lock.json
npm install
```

## 🐛 Устранение проблем

### Backend не запускается

```bash
# Проверить что порт свободен
lsof -i :8000

# Убить процесс
kill -9 $(lsof -t -i:8000)

# Или убить все Django процессы
pkill -9 -f "manage.py runserver"

# Очистить кеш и перезапустить
find . -name "*.pyc" -delete
python manage.py runserver
```

### Frontend не запускается

```bash
# Проверить что порт свободен
lsof -i :5173

# Убить процесс
kill -9 $(lsof -t -i:5173)

# Переустановить зависимости
cd skyfront
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Изменения не применяются

```bash
# 1. Убить все процессы
pkill -9 -f "manage.py runserver"

# 2. Очистить Python кеш
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 3. Перезапустить
python manage.py runserver
```

## 🧪 Тестирование

### Backend API

```bash
# Проверка endpoint (без токена)
curl -X POST http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/ \
  -H "Content-Type: application/json" \
  -d '{"course_id": 1, "grade_type": "1st_module", "grades": []}' \
  -w "\nStatus: %{http_code}\n"

# Ожидаем: 401 (не 404!) ✅
```

### Unit тесты

```bash
# Все тесты bulk update
python manage.py test result.tests.test_views -k bulk -v 2

# Конкретный тест
python manage.py test result.tests.test_views.ResultViewsTestCase.test_bulk_update_as_lecturer_success
```

### Диагностика URL

```bash
# Проверка URL routing
python test_bulk_update_url.py

# Детальная диагностика
python diagnose_urls.py
```

## 🔐 Работа с JWT токенами

### Получить токен

```bash
curl -X POST http://localhost:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

### Использовать токен

```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "course_id": 1,
    "grade_type": "1st_module",
    "grades": [
      {
        "student_id": 1,
        "attendance": 25.0,
        "activities": 30.0,
        "exam": 35.0
      }
    ]
  }'
```

### Проверить токен в браузере

```javascript
// Открыть Console (F12)

// Посмотреть токен
localStorage.getItem("access");

// Посмотреть всё хранилище
console.log({ ...localStorage });

// Удалить токен
localStorage.removeItem("access");
```

## 📁 Важные файлы

### Backend

- `result/views.py` - ViewSets и actions
- `result/urls.py` - URL routing
- `result/models.py` - Модели оценок
- `result/serializers.py` - DRF serializers
- `result/tests/test_views.py` - Unit тесты

### Frontend

- `skyfront/src/api.js` - Axios config + JWT interceptor
- `skyfront/src/constants.js` - Константы токенов
- `skyfront/src/pages/crud/teacher/TeacherGradesPage.jsx` - Bulk update UI

### Конфигурация

- `config/settings.py` - Django settings
- `skyfront/vite.config.js` - Vite config
- `skyfront/package.json` - NPM dependencies

## 📖 Документация

- `DOCS_INDEX.md` - Главный индекс документации
- `START_FULLSTACK.md` - Запуск проекта
- `FINAL_REPORT.md` - Итоговый отчет
- `result/BULK_UPDATE_FIX.md` - Исправление 404
- `skyfront/BULK_UPDATE_REFERENCE.md` - API справка

## 🌐 URLs

### Backend

- Admin: `http://localhost:8000/admin/`
- API: `http://localhost:8000/result/api/`
- Swagger: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

### Frontend

- App: `http://localhost:5173`

## 🎯 Bulk Update Endpoint

```
POST /result/api/lecturer/bulk-grades/bulk-update/
```

**⚠️ Важно:** `bulk-update` с ДЕФИСАМИ, не `bulk_update`!

## ✅ Checklist перед работой

- [ ] Backend запущен (`curl http://localhost:8000/admin/`)
- [ ] Frontend запущен (`curl http://localhost:5173`)
- [ ] Виртуальное окружение активировано
- [ ] Нет старых процессов Django
- [ ] Python кеш очищен

## 💡 Полезные алиасы

Добавьте в `~/.zshrc`:

```bash
# SkyLearn aliases
alias sky-backend='cd ~/Desktop/projects/SkyLearn && source venv/bin/activate && python manage.py runserver'
alias sky-frontend='cd ~/Desktop/projects/SkyLearn/skyfront && npm run dev'
alias sky-test='cd ~/Desktop/projects/SkyLearn && source venv/bin/activate && python manage.py test result.tests.test_views -k bulk -v 2'
alias sky-clean='cd ~/Desktop/projects/SkyLearn && find . -name "*.pyc" -delete && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null'
alias sky-kill='pkill -9 -f "manage.py runserver" && kill -9 $(lsof -t -i:5173) 2>/dev/null'
```

Использование:

```bash
sky-kill       # Убить все процессы
sky-clean      # Очистить кеш
sky-backend    # Запустить backend
sky-frontend   # Запустить frontend (в другом терминале)
sky-test       # Запустить тесты
```

## 🆘 Экстренная помощь

Если ничего не работает:

```bash
# 1. Убить ВСЁ
pkill -9 python
pkill -9 node

# 2. Очистить ВСЁ
cd ~/Desktop/projects/SkyLearn
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
cd skyfront
rm -rf node_modules package-lock.json

# 3. Переустановить ВСЁ
cd ..
source venv/bin/activate
pip install -r requirements.txt
cd skyfront
npm install

# 4. Запустить заново
cd ..
python manage.py runserver &
cd skyfront
npm run dev
```

---

**Всё работает?** → Читай `DOCS_INDEX.md` для деталей

**Что-то не работает?** → Читай `QUICK_FIX_DJANGO_RELOAD.md`

**Нужна помощь с API?** → Читай `skyfront/BULK_UPDATE_REFERENCE.md`
