# 🔒 Безопасная Аутентификация - Краткая Справка

## Что изменилось?

### Старо → Ново

| Было                      | Стало                     |
| ------------------------- | ------------------------- |
| Токены в localStorage     | Токены в httpOnly cookies |
| Уязвимость к XSS          | Защита от XSS             |
| Ручное обновление токенов | Автообновление            |
| Access token 60 минут     | Access token 15 минут     |
| Нет token rotation        | Token rotation включен    |

## Измененные Файлы

### Backend

```
accounts/
├── authentication.py     ← НОВЫЙ: Cookie auth
├── views.py              ← Secure login/refresh/logout views
├── urls.py               ← Добавлен /logout/
config/
└── settings.py           ← CORS + JWT настройки
```

### Frontend

```
skyfront/src/
├── api.js                ← withCredentials: true
├── componenets/
│   ├── Form.jsx          ← Без localStorage
│   └── ProtectedRoute.jsx ← Проверка через API
├── hooks/
│   └── useAuth.js        ← НОВЫЙ: хук для user info
└── App.jsx               ← Secure logout
```

## Как Запустить

### 1. Backend

```bash
cd /Users/adminbaike/Desktop/projects/SkyLearn
python manage.py runserver
```

### 2. Frontend

```bash
cd skyfront
npm run dev
```

### 3. Первый Вход

1. Откройте http://localhost:5173
2. Войдите в систему
3. Откройте DevTools → Application → Cookies
4. Увидите `access_token` и `refresh_token` с флагом HttpOnly ✓

## Ключевые Изменения

### Login (Form.jsx)

```javascript
// БЫЛО:
localStorage.setItem(ACCESS_TOKEN, res.data.access);

// СТАЛО:
// Ничего! Токены в cookies автоматически
```

### API Requests (api.js)

```javascript
// БЫЛО:
const token = localStorage.getItem(ACCESS_TOKEN);
config.headers.Authorization = `Bearer ${token}`;

// СТАЛО:
withCredentials: true; // Cookies отправляются автоматически
```

### Protected Route

```javascript
// БЫЛО:
const token = localStorage.getItem(ACCESS_TOKEN);
const decoded = jwtDecode(token);

// СТАЛО:
const response = await api.get("/accounts/profile/");
// Проверка через API, не через localStorage
```

## Endpoints

### POST /accounts/token/ (Login)

```json
Request:
{
  "username": "user",
  "password": "pass"
}

Response:
{
  "user": {...},
  "message": "Login successful"
}

Cookies:
- access_token (HttpOnly, 15 min)
- refresh_token (HttpOnly, 7 days)
```

### POST /accounts/token/refresh/ (Auto-Refresh)

```
No body needed!
Cookies sent automatically
```

### POST /accounts/logout/ (Logout)

```
Clears cookies on server
```

## Security Features

### ✅ Включено

1. **HttpOnly Cookies**

   - JavaScript не может читать токены
   - Защита от XSS

2. **SameSite=Lax**

   - Защита от CSRF
   - Cookies только для same-site requests

3. **Secure Flag (Production)**

   - Только HTTPS
   - Защита от перехвата

4. **Token Rotation**

   - Новый refresh token при каждом обновлении
   - Старые токены invalidated

5. **Auto-Refresh**

   - Происходит в фоне при 401
   - Пользователь не замечает

6. **Short Access Token**
   - 15 минут вместо 60
   - Меньше времени для атаки

## Testing

### Проверить Cookies

```javascript
// В DevTools Console
document.cookie;
// Не должно показывать access_token/refresh_token
```

### Проверить Auto-Refresh

1. Войдите
2. Подождите 15 минут
3. Сделайте запрос
4. Network tab покажет автоматический /token/refresh/

### Проверить Logout

1. Войдите
2. DevTools → Cookies (должны быть токены)
3. Нажмите Logout
4. Cookies должны исчезнуть

## Migration для Пользователей

Существующие пользователи должны:

1. Выйти (logout)
2. Войти заново (login)

Старые токены в localStorage будут игнорироваться.

## Production Checklist

- [ ] HTTPS включен
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS настроены
- [ ] CORS_ALLOWED_ORIGINS = ваш фронтенд
- [ ] Secure cookies включены
- [ ] Frontend API URL = production

## Quick Fixes

### CORS Error

```python
# settings.py
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS = True
```

### Cookies не сохраняются

```javascript
// api.js
axios.create({
  withCredentials: true, // ОБЯЗАТЕЛЬНО!
});
```

### 401 после refresh

- Проверьте логи сервера
- Возможно refresh token expired (7 дней)
- Нужен re-login

## Используйте useAuth Hook

```javascript
import { useAuth } from "../hooks/useAuth";

function MyComponent() {
  const { user, loading, role } = useAuth();

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <p>Hello, {user.first_name}!</p>
      <p>Role: {role}</p>
    </div>
  );
}
```

## Support

Если что-то не работает:

1. **Проверьте Console** - есть ли ошибки?
2. **Проверьте Network Tab** - запросы идут?
3. **Проверьте Cookies** - они устанавливаются?
4. **Проверьте Backend Logs** - есть ли ошибки?

## Документация

Полная документация: `SECURE_AUTH_GUIDE.md`

---

**Статус:** ✅ Готово к использованию  
**Безопасность:** 🛡️ Значительно улучшена  
**Дата:** 7 ноября 2025
