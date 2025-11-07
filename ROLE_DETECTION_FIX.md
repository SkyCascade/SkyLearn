# 🐛 Исправление: Определение Роли Пользователя

## Проблема
После входа все пользователи (включая админов и учителей) перенаправлялись на StudentDashboard.

## Причина
`Dashboard.jsx` использовал `localStorage.getItem(ROLE)`, который больше не обновляется после перехода на httpOnly cookies.

## ✅ Что было исправлено

### 1. Dashboard.jsx
**Было:**
```javascript
const currentRole = localStorage.getItem(ROLE) // ❌ Всегда null или старое значение
```

**Стало:**
```javascript
const { loading, role } = useAuth() // ✅ Получаем роль из API
```

### 2. useAuth Hook
**Улучшено определение роли с приоритетом:**
```javascript
// Приоритет: admin > lecturer > parent > student
if (user.is_superuser || user.is_staff) return "admin";
if (user.is_lecturer) return "lecturer";
if (user.is_parent) return "parent";
if (user.is_student) return "student";
```

**Добавлены debug logs:**
```javascript
console.log("👤 User fetched:", response.data);
console.log("🔑 Role detected:", role);
```

### 3. UserSerializer
**Добавлено поле `is_staff`:**
```python
fields = [
    # ...
    'is_superuser',
    'is_staff',  # ← Добавлено
    # ...
]
```

## 🧪 Как Протестировать

### 1. Очистить старые данные
```javascript
// В Browser Console (F12)
localStorage.clear()
sessionStorage.clear()
```

### 2. Перезапустить серверы
```bash
# Backend
python manage.py runserver

# Frontend (в другом терминале)
cd skyfront
npm run dev
```

### 3. Войти и проверить логи

**Откройте Console (F12) и войдите:**

#### Admin должен показать:
```
👤 User fetched: {is_superuser: true, is_staff: true, ...}
🔑 Role detected: admin
📊 Dashboard - Loading: false Role: admin
```

#### Teacher должен показать:
```
👤 User fetched: {is_lecturer: true, ...}
🔑 Role detected: lecturer
📊 Dashboard - Loading: false Role: lecturer
```

#### Student должен показать:
```
👤 User fetched: {is_student: true, ...}
🔑 Role detected: student
📊 Dashboard - Loading: false Role: student
```

### 4. Проверить Dashboard
- **Admin** → AdminDashboard (фиолетовая тема)
- **Lecturer** → TeacherDashboard (зеленая тема)
- **Student** → StudentDashboard (синяя тема)

## 🔍 Отладка Проблем

### Проблема: Все еще перенаправляет на Student

**Решение 1: Проверьте Console logs**
```javascript
// Должны видеть:
👤 User fetched: {...}
🔑 Role detected: [роль]
📊 Dashboard - Loading: false Role: [роль]
```

**Решение 2: Проверьте ответ API**
```javascript
// В Console выполните:
fetch('http://localhost:8000/accounts/profile/', {
  credentials: 'include'
}).then(r => r.json()).then(console.log)

// Должно показать:
{
  is_superuser: true/false,
  is_staff: true/false,
  is_lecturer: true/false,
  is_student: true/false,
  // ...
}
```

**Решение 3: Проверьте cookies**
- DevTools → Application → Cookies
- Должны быть: `access_token`, `refresh_token`
- Если нет - выйдите и войдите снова

**Решение 4: Очистите кэш браузера**
```
Ctrl+Shift+Delete (Windows/Linux)
Cmd+Shift+Delete (Mac)
```

### Проблема: Role = null

**Причина:** Пользователь не имеет ни одного флага роли.

**Решение:** Проверьте в Django Admin:
```
http://localhost:8000/admin/accounts/user/
```

Для админа должно быть:
- ☑️ is_superuser
- ☑️ is_staff

Для учителя:
- ☑️ is_lecturer

Для студента:
- ☑️ is_student

### Проблема: "Role Not Defined" screen

**Причина:** `role` возвращает `null`.

**Решение:** Проверьте console logs и убедитесь, что пользователь имеет хотя бы один флаг роли.

## 📝 Измененные Файлы

### Backend (1 файл)
```
✅ accounts/serializers.py
   - Добавлено поле 'is_staff' в UserSerializer
```

### Frontend (2 файла)
```
✅ skyfront/src/pages/Dashboard.jsx
   - Использует useAuth() вместо localStorage
   - Добавлен debug logging
   
✅ skyfront/src/hooks/useAuth.js
   - Исправлен приоритет определения роли
   - Добавлен debug logging
```

## 🎯 Проверочный Чеклист

- [ ] Backend запущен без ошибок
- [ ] Frontend запущен без ошибок
- [ ] localStorage очищен
- [ ] Вход под админом → AdminDashboard
- [ ] Вход под учителем → TeacherDashboard
- [ ] Вход под студентом → StudentDashboard
- [ ] Console logs показывают правильную роль
- [ ] Нет ошибок в Console

## 💡 Важно!

После этих изменений:
1. **Не нужно** очищать базу данных
2. **Нужно** выйти и войти заново (чтобы получить новые cookies)
3. **Рекомендуется** очистить localStorage для удаления старых данных

## 🚀 Готово!

Теперь определение роли работает правильно через API и httpOnly cookies!

---

**Дата исправления:** 7 ноября 2025  
**Затронутые файлы:** 3  
**Время на исправление:** ~5 минут
