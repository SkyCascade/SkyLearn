# Быстрая проверка исправления

## ✅ Что было исправлено

Изменены API пути с `/api/attendance/...` на `/attendance/...`

## 🔍 Как проверить

### 1. Откройте DevTools (F12)

### 2. Перейдите на вкладку Network

### 3. Откройте страницу Lesson Times

http://localhost:5174/admin/lesson-times

### 4. Проверьте запросы

Должны быть **успешные** запросы (зеленые, 200 OK):

```
✅ GET /attendance/lesson-times/  →  200 OK
```

Если видите:

```
❌ GET /api/attendance/lesson-times/  →  404 Not Found
```

Значит еще остались старые пути.

### 5. Попробуйте создать время урока

**Форма:**

- Номер урока: 1
- Время начала: 09:00
- Время окончания: 10:30

**Нажмите "Добавить"**

**Проверьте в Network:**

```
✅ POST /attendance/lesson-times/  →  201 Created
✅ GET /attendance/lesson-times/   →  200 OK (reload)
```

### 6. Проверьте страницу расписания

http://localhost:5174/admin/schedule

**Должны загрузиться:**

```
✅ GET /attendance/schedules/       →  200 OK
✅ GET /programs/api/course/        →  200 OK
✅ GET /accounts/api/groups/        →  200 OK
✅ GET /attendance/lesson-times/    →  200 OK
```

## 📊 Ожидаемый результат

- Страница lesson-times загружается без ошибок
- Можно создавать времена уроков
- Dropdown в расписании показывает созданные времена
- Нет ошибок 404 или 500 в консоли

## 🐛 Если все еще есть ошибки

1. **Очистите кеш браузера** (Ctrl+Shift+R или Cmd+Shift+R)
2. **Перезапустите frontend сервер**:
   ```bash
   cd /Users/adminbaike/Desktop/projects/SkyLearn/skyfront
   npm run dev
   ```
3. **Проверьте что backend запущен**:
   ```bash
   curl http://localhost:8000/attendance/lesson-times/
   ```

## ✨ Все работает если

- ✅ Страница загружается
- ✅ Форма отправляется
- ✅ Данные сохраняются
- ✅ Список обновляется
- ✅ Нет ошибок в консоли

---

**Дата исправления:** 20 ноября 2025 г.
**Статус:** ✅ Готово
