# 🔧 Quick Fix: Определение Роли

## Проблема
Все пользователи попадают на StudentDashboard ❌

## Решение
Обновлен Dashboard для работы с новой системой аутентификации ✅

## Что Делать

### 1. Перезапустите приложение
```bash
# Backend (если уже запущен - перезапускать не нужно)
python manage.py runserver

# Frontend (если запущен - перезапустить)
Ctrl+C
npm run dev
```

### 2. Очистите localStorage
**В браузере:**
- F12 → Console
- Выполните: `localStorage.clear()`

### 3. Выйдите и войдите снова
- Нажмите Logout
- Войдите с вашими credentials

### 4. Проверьте Console (F12)
Должны увидеть:
```
👤 User fetched: {is_superuser: true, ...}
🔑 Role detected: admin (или lecturer/student)
📊 Dashboard - Loading: false Role: admin
```

## Ожидаемый Результат

| Роль | Dashboard | Цвет темы |
|------|-----------|-----------|
| Admin | AdminDashboard | Фиолетовый |
| Lecturer | TeacherDashboard | Зеленый |
| Student | StudentDashboard | Синий |

## Если Не Работает

### Проверка 1: API Response
```javascript
// В Console:
fetch('http://localhost:8000/accounts/profile/', {
  credentials: 'include'
}).then(r => r.json()).then(console.log)
```

Должно показать поля:
- `is_superuser`
- `is_staff`
- `is_lecturer`
- `is_student`

### Проверка 2: Cookies
DevTools → Application → Cookies
- ✅ access_token (HttpOnly)
- ✅ refresh_token (HttpOnly)

### Проверка 3: Django Admin
http://localhost:8000/admin/accounts/user/

**Для админа:**
- ☑️ Superuser status
- ☑️ Staff status

**Для учителя:**
- ☑️ is_lecturer

**Для студента:**
- ☑️ is_student

## Готово! 🎉

После выхода и входа роль должна определяться правильно.

---

**Документация:** `ROLE_DETECTION_FIX.md`
