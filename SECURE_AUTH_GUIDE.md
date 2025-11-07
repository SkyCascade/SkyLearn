# 🔒 Руководство по Безопасной Аутентификации

## Обзор изменений

Мы полностью переработали систему аутентификации для повышения безопасности. Основные улучшения:

### ❌ Старый подход (НЕБЕЗОПАСНЫЙ)

- JWT токены хранились в `localStorage`
- Уязвимость к XSS атакам
- Токены доступны JavaScript коду
- Нет автоматического обновления токенов

### ✅ Новый подход (БЕЗОПАСНЫЙ)

- JWT токены в **httpOnly cookies**
- Защита от XSS атак
- Автоматическое обновление токенов
- Refresh token rotation
- SameSite cookie protection
- CORS правильно настроен

---

## 🛡️ Что изменилось?

### Backend (Django)

#### 1. Новый Authentication Backend

**Файл:** `accounts/authentication.py`

```python
class JWTCookieAuthentication(JWTAuthentication):
    """Читает JWT из httpOnly cookies вместо заголовка"""
```

- Проверяет токены в cookies
- Fallback на Authorization header (для обратной совместимости)

#### 2. Новые Secure Views

**Файл:** `accounts/views.py`

**`CustomTokenObtainPairView`** (Login):

- Устанавливает access_token и refresh_token в httpOnly cookies
- Возвращает только user data (без токенов в JSON)
- Настройки cookies: httpOnly, secure (в production), SameSite=Lax

**`SecureTokenRefreshView`** (Refresh):

- Читает refresh_token из cookie
- Обновляет access_token
- Поддерживает token rotation

**`LogoutView`** (Logout):

- Очищает cookies на сервере
- Безопасный выход

#### 3. Настройки (settings.py)

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Короткий срок жизни
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,  # Token rotation включен!
    'BLACKLIST_AFTER_ROTATION': True,

    # Cookie настройки
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_REFRESH': 'refresh_token',
    'AUTH_COOKIE_SECURE': not DEBUG,  # True в production (HTTPS)
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_SAMESITE': 'Lax',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.authentication.JWTCookieAuthentication',  # Наш кастомный
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Fallback
    ),
}
```

### Frontend (React)

#### 1. API Configuration

**Файл:** `skyfront/src/api.js`

```javascript
const api = axios.create({
  baseURL: apiUrl,
  withCredentials: true, // ВАЖНО! Отправляет cookies
});
```

- **Удалены** все обращения к `localStorage`
- **Добавлен** `withCredentials: true`
- **Автоматическое** обновление токенов через interceptor

#### 2. Форма входа

**Файл:** `skyfront/src/componenets/Form.jsx`

- Больше **не сохраняет** токены в localStorage
- Токены автоматически в cookies
- Улучшен UI с обработкой ошибок

#### 3. Protected Route

**Файл:** `skyfront/src/componenets/ProtectedRoute.jsx`

- Проверяет авторизацию через API запрос
- Автоматическое обновление токена при 401
- Красивый Loading screen

#### 4. Logout

**Файл:** `skyfront/src/App.jsx`

- Вызывает `/accounts/logout/` для очистки cookies
- Очищает sessionStorage
- Редирект на login

#### 5. Custom Hook

**Файл:** `skyfront/src/hooks/useAuth.js`

```javascript
const { user, loading, role } = useAuth();
```

Для получения информации о пользователе из API.

---

## 🔐 Преимущества Безопасности

### 1. HttpOnly Cookies

```
Set-Cookie: access_token=xxx; HttpOnly; Secure; SameSite=Lax
```

- ❌ JavaScript **НЕ МОЖЕТ** получить доступ к токену
- ✅ Защита от XSS атак
- ✅ Браузер автоматически управляет cookies

### 2. Secure Flag (Production)

```
Set-Cookie: access_token=xxx; Secure
```

- ✅ Cookies передаются только через HTTPS
- ❌ HTTP запросы не получат токен

### 3. SameSite=Lax

```
Set-Cookie: access_token=xxx; SameSite=Lax
```

- ✅ Защита от CSRF атак
- ✅ Cookies не отправляются с cross-site запросами

### 4. Token Rotation

```python
'ROTATE_REFRESH_TOKENS': True
```

- ✅ При каждом refresh выдается новый refresh token
- ✅ Старые токены invalidated
- ✅ Защита от token replay attacks

### 5. Короткий Access Token (15 минут)

```python
'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15)
```

- ✅ Минимизирует window of attack
- ✅ Automatic refresh в background

---

## 📋 Миграция с Старой Системы

### Шаг 1: Backend

```bash
# Ничего не нужно делать с базой данных
# Просто перезапустите сервер
python manage.py runserver
```

### Шаг 2: Frontend

```bash
cd skyfront
npm install  # На случай новых зависимостей
npm run dev
```

### Шаг 3: Для Существующих Пользователей

Пользователям нужно будет:

1. Выйти из системы (logout)
2. Войти заново (login)

**Старые токены** в localStorage будут игнорироваться.

---

## 🧪 Тестирование

### 1. Проверка Cookies в DevTools

1. Откройте DevTools (F12)
2. Перейдите в Application → Cookies
3. После login должны появиться:
   - `access_token` (HttpOnly: ✓)
   - `refresh_token` (HttpOnly: ✓)

### 2. Проверка XSS Protection

Откройте Console и попробуйте:

```javascript
document.cookie;
// Не должно показывать access_token и refresh_token
```

### 3. Проверка Auto-Refresh

1. Подождите 15 минут (или измените ACCESS_TOKEN_LIFETIME на 1 минуту для теста)
2. Сделайте любой запрос
3. В Network tab должен появиться автоматический `/accounts/token/refresh/`

### 4. Проверка Logout

1. Войдите в систему
2. Нажмите Logout
3. Проверьте cookies - они должны быть удалены
4. Попробуйте зайти на защищенную страницу - должен redirect на /login

---

## 🚀 Production Deployment

### Django Settings

```python
# В production обязательно:
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# CORS - только ваш фронтенд
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]

# HTTPS обязателен для Secure cookies
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Frontend

```javascript
// В production измените API URL
const apiUrl = "https://api.yourdomain.com";
```

### HTTPS

**ОБЯЗАТЕЛЬНО** использовать HTTPS в production для:

- Secure cookies
- Защиты от man-in-the-middle атак

---

## 🔍 Troubleshooting

### Проблема: Cookies не устанавливаются

**Причины:**

1. `withCredentials: true` не установлен в axios
2. CORS не разрешает credentials
3. Frontend и Backend на разных доменах без правильной настройки

**Решение:**

```javascript
// Frontend
axios.create({
  withCredentials: true,
});

// Backend
CORS_ALLOW_CREDENTIALS = True;
```

### Проблема: 401 Unauthorized

**Причины:**

1. Access token истек
2. Refresh token invalid

**Решение:**

- Проверьте автоматический refresh в api interceptor
- Проверьте, что cookies отправляются

### Проблема: CORS ошибка

**Решение:**

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Или ваш порт
]
CORS_ALLOW_CREDENTIALS = True
```

---

## 📊 Сравнение Безопасности

| Аспект               | localStorage (Старый) | httpOnly Cookies (Новый) |
| -------------------- | --------------------- | ------------------------ |
| **XSS Protection**   | ❌ Уязвимо            | ✅ Защищено              |
| **CSRF Protection**  | ✅ Нет проблемы       | ✅ SameSite=Lax          |
| **Token Visibility** | ❌ Виден в JS         | ✅ Скрыт от JS           |
| **Auto Refresh**     | ❌ Нет                | ✅ Есть                  |
| **Token Rotation**   | ❌ Нет                | ✅ Есть                  |
| **HTTPS Required**   | ⚠️ Рекомендуется      | ✅ Обязательно           |

---

## 🎯 Best Practices

### ✅ DO (Делайте)

1. **Используйте HTTPS** в production
2. **Короткий Access Token** (15 минут)
3. **Длинный Refresh Token** (7 дней)
4. **Token Rotation** включен
5. **SameSite=Lax** для cookies
6. **CORS правильно настроен**
7. **Регулярно обновляйте зависимости**

### ❌ DON'T (Не делайте)

1. ❌ Не храните токены в localStorage
2. ❌ Не отключайте httpOnly
3. ❌ Не используйте HTTP в production
4. ❌ Не отключайте CORS validation
5. ❌ Не делайте слишком длинные Access Tokens
6. ❌ Не логируйте токены
7. ❌ Не отправляйте токены в URL parameters

---

## 📚 Дополнительные Ресурсы

### OWASP Guidelines

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

### JWT Best Practices

- [JWT.io Best Practices](https://jwt.io/introduction)
- [RFC 8725: JWT Best Current Practices](https://datatracker.ietf.org/doc/html/rfc8725)

---

## 🎉 Итоги

Теперь ваша система аутентификации:

✅ **Защищена** от XSS атак  
✅ **Защищена** от CSRF атак  
✅ **Автоматически** обновляет токены  
✅ **Использует** token rotation  
✅ **Следует** industry best practices  
✅ **Готова** к production deployment

**Ваше приложение стало значительно безопаснее!** 🎊

---

**Дата:** 7 ноября 2025  
**Версия:** 2.0 - Secure Authentication
