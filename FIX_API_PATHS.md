# Исправление ошибки 500 - API пути

## Проблема

При загрузке страницы управления расписанием возникала ошибка 500 (Internal Server Error):

```
Failed to load resource: the server responded with a status of 500 (Internal Server Error)
[20/Nov/2025 10:39:41] "GET /attendance/schedules/ HTTP/1.1" 401 58
[20/Nov/2025 10:39:41] "POST /accounts/token/refresh/ HTTP/1.1" 200 42
[20/Nov/2025 10:39:41] "GET /attendance/schedules/ HTTP/1.1" 200 452
[20/Nov/2025 10:39:41] "GET /programs/api/course/ HTTP/1.1" 200 2
[20/Nov/2025 10:39:41] "GET /accounts/api/groups/ HTTP/1.1" 200 2
```

## Причина

В компонентах `AdminSchedule.jsx` и `LessonTimes.jsx` использовались неправильные пути API с префиксом `/api/`:

```javascript
// ❌ Неправильно
await api.get("/api/attendance/lesson-times/");
await api.post("/api/attendance/lesson-times/", data);

// ❌ Неправильно
await api.get("/api/attendance/schedules/");
```

## Решение

### URL структура Django

Согласно `config/urls.py`:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("programs/", include("course.urls")),
    path("result/", include("result.urls")),
    path("attendance/", include("attendance.urls")),
]
```

Правильные пути **БЕЗ** префикса `/api/`:

```javascript
// ✅ Правильно
await api.get("/attendance/lesson-times/");
await api.post("/attendance/lesson-times/", data);
await api.put("/attendance/lesson-times/${id}/", data);
await api.delete("/attendance/lesson-times/${id}/");

// ✅ Правильно
await api.get("/attendance/schedules/");
await api.post("/attendance/schedules/", data);
await api.put("/attendance/schedules/${id}/", data);
await api.delete("/attendance/schedules/${id}/");
```

### Файлы исправлены

#### 1. `AdminSchedule.jsx`

**Строки изменены:**

- Строка 30: `api.get("/attendance/schedules/")`
- Строка 36: `api.get("/programs/api/course/")`
- Строка 45: `api.get("/accounts/api/groups/")`
- Строка 54: `api.get("/attendance/lesson-times/")`
- Строка 133: `api.put("/attendance/schedules/${editingSchedule.id}/")`
- Строка 140: `api.post("/attendance/schedules/")`
- Строка 178: `api.delete("/attendance/schedules/${scheduleId}/")`

#### 2. `LessonTimes.jsx`

**Строки изменены:**

- Строка 22: `api.get('/attendance/lesson-times/')`
- Строка 61: `api.post('/attendance/lesson-times/', formData)`
- Строка 77: `api.put('/attendance/lesson-times/${editingId}/', formData)`
- Строка 96: `api.delete('/attendance/lesson-times/${id}/')`

### Обновлена документация

Исправлены пути API в:

- ✅ `LESSON_TIME_FRONTEND_GUIDE.md`
- ✅ `TESTING_LESSON_TIME_FRONTEND.md`
- ✅ `LESSON_TIME_FRONTEND_SUMMARY.md`

## Правильная конфигурация

### axios api.js

```javascript
const apiUrl = "http://localhost:8000";

const api = axios.create({
  baseURL: apiUrl, // http://localhost:8000
  withCredentials: true,
});
```

### Итоговые URL

При вызове `api.get('/attendance/lesson-times/')` axios формирует:

```
http://localhost:8000/attendance/lesson-times/
```

## Проверка

После исправления в консоли браузера (F12 → Network) должны быть успешные запросы:

```
✅ GET  http://localhost:8000/attendance/schedules/        → 200 OK
✅ GET  http://localhost:8000/programs/api/course/         → 200 OK
✅ GET  http://localhost:8000/accounts/api/groups/         → 200 OK
✅ GET  http://localhost:8000/attendance/lesson-times/     → 200 OK
✅ POST http://localhost:8000/attendance/lesson-times/     → 201 Created
✅ PUT  http://localhost:8000/attendance/lesson-times/1/   → 200 OK
✅ DELETE http://localhost:8000/attendance/lesson-times/1/ → 204 No Content
```

## Статус

✅ **Исправлено**

Все API пути обновлены и соответствуют URL структуре Django.
