# 🚀 Запуск Full Stack приложения SkyLearn

## ⚡ Быстрый старт

### Терминал 1: Backend (Django)

```bash
cd /Users/adminbaike/Desktop/projects/SkyLearn
source venv/bin/activate
python manage.py runserver
```

Откроется на: `http://localhost:8000`

### Терминал 2: Frontend (React + Vite)

```bash
cd /Users/adminbaike/Desktop/projects/SkyLearn/skyfront
npm run dev
```

Откроется на: `http://localhost:5173`

## 📋 Полная последовательность первого запуска

### 1. Подготовка Backend

```bash
# Перейти в корень проекта
cd /Users/adminbaike/Desktop/projects/SkyLearn

# Активировать виртуальное окружение
source venv/bin/activate

# Убедиться что все зависимости установлены
pip install -r requirements.txt

# Применить миграции (если нужно)
python manage.py migrate

# Создать суперпользователя (если еще не создан)
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

**Проверка:** Откройте `http://localhost:8000/admin` - должна открыться админка Django

### 2. Подготовка Frontend

```bash
# Перейти в папку фронтенда
cd /Users/adminbaike/Desktop/projects/SkyLearn/skyfront

# Установить зависимости (только первый раз)
npm install

# Запустить dev сервер
npm run dev
```

**Проверка:** Откройте `http://localhost:5173` - должно открыться React приложение

## 🔍 Проверка работоспособности

### 1. Проверка Backend

```bash
# Проверить что Django работает
curl http://localhost:8000/admin/
# Должен вернуть HTML страницу

# Проверить bulk-update endpoint
curl -X POST http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/ \
  -H "Content-Type: application/json" \
  -d '{"course_id": 1, "grade_type": "1st_module", "grades": []}' \
  -w "\nStatus: %{http_code}\n"
# Должен вернуть: 401 (требует токен) ✅
```

### 2. Проверка Frontend

Откройте DevTools (F12) → Console:

```javascript
// Проверить что API настроен правильно
console.log(import.meta.env);

// Проверить токен
console.log("Token:", localStorage.getItem("access"));
```

### 3. Проверка интеграции

1. Откройте `http://localhost:5173`
2. Залогиньтесь как преподаватель
3. Перейдите на страницу оценок
4. Попробуйте сохранить оценки
5. Проверьте Network tab (F12) → должен быть запрос к `bulk-update` с токеном

## 🛠️ Скрипт для одновременного запуска (macOS/Linux)

Создайте файл `start.sh` в корне проекта:

```bash
#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting SkyLearn Full Stack...${NC}"

# Функция для остановки всех процессов при выходе
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping all services...${NC}"
    pkill -P $$ # Убить все дочерние процессы
    exit 0
}

trap cleanup SIGINT SIGTERM

# Запуск Backend
echo -e "${GREEN}📡 Starting Backend (Django)...${NC}"
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!

# Подождать пока backend запустится
sleep 3

# Проверить что backend запущен
if curl -s http://localhost:8000/admin/ > /dev/null; then
    echo -e "${GREEN}✅ Backend started successfully${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    cleanup
fi

# Запуск Frontend
echo -e "${GREEN}💻 Starting Frontend (React + Vite)...${NC}"
cd skyfront
npm run dev &
FRONTEND_PID=$!

# Подождать пока frontend запустится
sleep 3

echo -e "${GREEN}✅ Full Stack started!${NC}"
echo -e "${YELLOW}Backend:${NC}  http://localhost:8000"
echo -e "${YELLOW}Frontend:${NC} http://localhost:5173"
echo -e "${YELLOW}Admin:${NC}    http://localhost:8000/admin"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Ожидать завершения
wait
```

Сделайте файл исполняемым и запустите:

```bash
chmod +x start.sh
./start.sh
```

## 📝 Переменные окружения

### Backend (.env)

Создайте файл `.env` в корне проекта:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173

# Database (если используете PostgreSQL)
DB_NAME=skylearn
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### Frontend (.env)

Создайте файл `.env` в папке `skyfront/`:

```env
VITE_API_URL=http://localhost:8000
```

Используйте в коде:

```javascript
const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

## ⚠️ Troubleshooting

### Backend не запускается

```bash
# Проверить что порт 8000 свободен
lsof -i :8000

# Убить процесс на порту 8000
kill -9 $(lsof -t -i:8000)

# Проверить виртуальное окружение
which python  # Должен показать путь в venv
```

### Frontend не запускается

```bash
# Проверить что порт 5173 свободен
lsof -i :5173

# Убить процесс на порту 5173
kill -9 $(lsof -t -i:5173)

# Переустановить зависимости
cd skyfront
rm -rf node_modules package-lock.json
npm install
```

### CORS ошибки

Добавьте в `config/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Добавить в начало
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True
```

## ✅ Checklist

- [ ] Python 3.11+ установлен
- [ ] Node.js 18+ установлен
- [ ] Виртуальное окружение создано и активировано
- [ ] Backend зависимости установлены
- [ ] Frontend зависимости установлены
- [ ] База данных мигрирована
- [ ] Суперпользователь создан
- [ ] Backend запущен на порту 8000
- [ ] Frontend запущен на порту 5173
- [ ] CORS настроен
- [ ] Bulk update endpoint возвращает 401 (не 404)

## 🎯 После запуска

1. **Backend Admin:** `http://localhost:8000/admin`
2. **Frontend:** `http://localhost:5173`
3. **API Docs (Swagger):** `http://localhost:8000/api/schema/swagger-ui/`
4. **API Docs (ReDoc):** `http://localhost:8000/api/schema/redoc/`

Теперь все должно работать! 🎉
