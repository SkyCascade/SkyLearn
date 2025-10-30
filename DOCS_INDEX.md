# 📚 SkyLearn - Documentation Index

## 🎯 Быстрый старт

### Для разработчиков

1. **[START_FULLSTACK.md](START_FULLSTACK.md)** - Запуск backend + frontend одновременно
2. **[skyfront/SETUP.md](skyfront/SETUP.md)** - Подробная настройка фронтенда

### Для работы с Bulk Update

1. **[skyfront/BULK_UPDATE_REFERENCE.md](skyfront/BULK_UPDATE_REFERENCE.md)** - Быстрая справка по API
2. **[result/BULK_UPDATE_FIX.md](result/BULK_UPDATE_FIX.md)** - История исправления 404 ошибки

## 📁 Структура документации

### 🚀 Setup & Configuration

- **START_FULLSTACK.md** - Полный гайд по запуску проекта
- **skyfront/SETUP.md** - Настройка фронтенда (React + Vite)
- **QUICK_FIX_DJANGO_RELOAD.md** - Решение проблем с перезагрузкой Django

### 🔧 Backend (Django)

- **result/BULK_UPDATE_FIX.md** - Исправление URL routing для bulk-update
- **result/WHY_401_AND_404.md** - Анализ: почему возвращаются разные HTTP коды
- **result/TESTING_AND_FIXES.md** - Тесты и технические детали

### 💻 Frontend (React)

- **skyfront/BULK_UPDATE_REFERENCE.md** - API справочник для bulk-update
- **skyfront/SETUP.md** - Настройка и структура фронтенда

### 🐛 Troubleshooting

- **QUICK_FIX_DJANGO_RELOAD.md** - Когда изменения не применяются
- **result/WHY_401_AND_404.md** - Диагностика HTTP ошибок
- **QUICK_FIX_401.md** - Решение проблем с аутентификацией

## 🎯 По задачам

### Нужно запустить проект?

→ [START_FULLSTACK.md](START_FULLSTACK.md)

### Проблемы с 404 на bulk-update?

→ [result/BULK_UPDATE_FIX.md](result/BULK_UPDATE_FIX.md)

### Изменения в коде не применяются?

→ [QUICK_FIX_DJANGO_RELOAD.md](QUICK_FIX_DJANGO_RELOAD.md)

### Нужна документация API?

→ [skyfront/BULK_UPDATE_REFERENCE.md](skyfront/BULK_UPDATE_REFERENCE.md)

### Настроить фронтенд?

→ [skyfront/SETUP.md](skyfront/SETUP.md)

### Разобраться почему 401/404?

→ [result/WHY_401_AND_404.md](result/WHY_401_AND_404.md)

## 📊 Архитектура проекта

```
SkyLearn/
├── Backend (Django)
│   ├── config/          # Django settings
│   ├── accounts/        # User management
│   ├── core/           # Core functionality
│   ├── course/         # Course management
│   ├── result/         # ✅ Grades & Bulk Update
│   └── manage.py
│
└── Frontend (React + Vite)
    └── skyfront/
        ├── src/
        │   ├── api.js              # ✅ Axios + JWT
        │   ├── constants.js        # ✅ Token keys
        │   ├── pages/
        │   │   └── crud/teacher/
        │   │       └── TeacherGradesPage.jsx  # ✅ Bulk Update
        │   └── components/
        └── package.json
```

## 🔑 Ключевые компоненты

### Backend

**Endpoint:** `POST /result/api/lecturer/bulk-grades/bulk-update/`

**Файл:** `result/views.py`

```python
@action(detail=False, methods=['post'], url_path='bulk-update')
def bulk_update(self, request):
    # Массовое обновление оценок
```

**Тесты:** `result/tests/test_views.py` (9 тестов, все проходят ✅)

### Frontend

**API Client:** `skyfront/src/api.js`

```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Component:** `skyfront/src/pages/crud/teacher/TeacherGradesPage.jsx`

```javascript
await api.post('result/api/lecturer/bulk-grades/bulk-update/', {
  course_id: 1,
  grade_type: '1st_module',
  grades: [...]
});
```

## ✅ Статус

| Компонент          | Статус            | Проверка                                                                 |
| ------------------ | ----------------- | ------------------------------------------------------------------------ |
| Backend API        | ✅ Работает       | `curl localhost:8000/result/api/lecturer/bulk-grades/bulk-update/` → 401 |
| URL Routing        | ✅ Исправлено     | `url_path='bulk-update'` добавлен                                        |
| Unit Tests         | ✅ 9/9 пройдены   | `python manage.py test result.tests.test_views -k bulk`                  |
| Frontend API       | ✅ Настроен       | JWT interceptor добавлен в `api.js`                                      |
| Frontend Component | ✅ Правильный URL | `bulk-update` с дефисами                                                 |
| Authentication     | ✅ JWT токены     | Сохраняются в localStorage                                               |

## 🚀 Быстрые команды

```bash
# Backend
cd /Users/adminbaike/Desktop/projects/SkyLearn
source venv/bin/activate
python manage.py runserver

# Frontend
cd /Users/adminbaike/Desktop/projects/SkyLearn/skyfront
npm run dev

# Tests
python manage.py test result.tests.test_views -k bulk -v 2

# Проверка endpoint
curl -X POST http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/ \
  -H "Content-Type: application/json" \
  -d '{}' -w "\nStatus: %{http_code}\n"
```

## 📖 Дополнительная документация

- **README.md** - Основная документация проекта
- **TODO.md** - Планы развития
- **CONTRIBUTING.md** - Гайд для контрибьюторов
- **CODE_OF_CONDUCT.md** - Правила поведения

## 🔗 API Endpoints

### Production

- **Swagger UI:** `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc:** `http://localhost:8000/api/schema/redoc/`
- **Admin Panel:** `http://localhost:8000/admin/`

### Development

- **Backend:** `http://localhost:8000`
- **Frontend:** `http://localhost:5173`

## 💡 Полезные ссылки

- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Material-UI](https://mui.com/)
- [JWT Authentication](https://jwt.io/)

## 📞 Контакты

- **Repository:** [Adilhan434/SkyLearn-1](https://github.com/Adilhan434/SkyLearn-1)
- **Branch:** `moveToApi`

---

**Последнее обновление:** 30 октября 2025 г.

**Версия документации:** 1.0.0

✅ Все компоненты протестированы и работают!
