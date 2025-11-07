# ✅ Чеклист Миграции на Безопасную Аутентификацию

## Подготовка

### Backend

- [ ] Все изменения в `accounts/authentication.py` применены
- [ ] Все изменения в `accounts/views.py` применены
- [ ] Все изменения в `accounts/urls.py` применены
- [ ] Все изменения в `config/settings.py` применены
- [ ] Нет ошибок Python syntax

### Frontend

- [ ] Все изменения в `api.js` применены
- [ ] Все изменения в `Form.jsx` применены
- [ ] Все изменения в `ProtectedRoute.jsx` применены
- [ ] Все изменения в `App.jsx` применены
- [ ] Создан `hooks/useAuth.js`
- [ ] Нет ошибок JavaScript syntax

## Первый Запуск

### 1. Backend Start

```bash
cd /Users/adminbaike/Desktop/projects/SkyLearn
python manage.py runserver
```

Проверить:

- [ ] Сервер запустился без ошибок
- [ ] Нет предупреждений в консоли
- [ ] API доступен на http://localhost:8000

### 2. Frontend Start

```bash
cd skyfront
npm run dev
```

Проверить:

- [ ] Dev server запустился
- [ ] Нет ошибок компиляции
- [ ] Приложение доступно на http://localhost:5173

## Тестирование Функциональности

### Login

- [ ] Открыть http://localhost:5173/login
- [ ] Ввести credentials
- [ ] Нажать Login
- [ ] Должен быть redirect на главную
- [ ] В DevTools → Application → Cookies должны быть:
  - [ ] `access_token` (HttpOnly: ✓)
  - [ ] `refresh_token` (HttpOnly: ✓)

### Protected Routes

- [ ] Главная страница загружается
- [ ] Профиль студента/учителя/админа работает
- [ ] Все API запросы проходят
- [ ] В Network tab видно что cookies отправляются

### Security Check

- [ ] В Console выполнить: `document.cookie`
- [ ] НЕ должно показывать `access_token` и `refresh_token`
- [ ] В DevTools → Application → Local Storage
- [ ] НЕ должно быть старых токенов

### Auto-Refresh (Опционально)

Для быстрого теста измените в `settings.py`:

```python
'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1),
```

Затем:

- [ ] Войти в систему
- [ ] Подождать 1 минуту
- [ ] Сделать любой запрос (открыть другую страницу)
- [ ] В Network tab должен появиться `/accounts/token/refresh/`
- [ ] Запрос должен пройти успешно

Вернуть обратно:

```python
'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
```

### Logout

- [ ] Нажать кнопку Logout
- [ ] Должен быть redirect на /login
- [ ] Cookies должны исчезнуть из DevTools
- [ ] Попытка зайти на защищенную страницу → redirect на /login

## Миграция Существующих Пользователей

### Инструкция для Пользователей:

1. Выйти из системы (если залогинены)
2. Очистить localStorage (опционально):
   - DevTools → Console
   - `localStorage.clear()`
3. Войти заново

### Уведомление:

```
⚠️ Внимание!
Мы улучшили безопасность системы.
Пожалуйста, выйдите и войдите заново.
```

## Проверка Безопасности

### XSS Protection

- [ ] Console → `document.cookie` не показывает токены
- [ ] Console → `localStorage.getItem('access')` возвращает null
- [ ] Токены в DevTools помечены как HttpOnly

### CSRF Protection

- [ ] SameSite=Lax установлен
- [ ] Cookies только для same-origin requests

### HTTPS (Production)

- [ ] Secure flag включен (когда DEBUG=False)
- [ ] HTTPS используется в production

## Production Deployment

### Backend Configuration

```python
# settings.py для production

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SIMPLE_JWT = {
    'AUTH_COOKIE_SECURE': True,  # Обязательно в production
    # ... остальные настройки
}
```

Checklist:

- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS настроены
- [ ] CORS_ALLOWED_ORIGINS = production frontend
- [ ] HTTPS включен
- [ ] Secure cookies включены

### Frontend Configuration

```javascript
// api.js для production
const apiUrl = "https://api.yourdomain.com";
```

Checklist:

- [ ] API URL = production backend
- [ ] Build работает: `npm run build`
- [ ] Preview работает: `npm run preview`

## Rollback Plan (на случай проблем)

### Если что-то пошло не так:

1. **Backend Rollback:**

```bash
git checkout HEAD~1 -- accounts/authentication.py
git checkout HEAD~1 -- accounts/views.py
git checkout HEAD~1 -- accounts/urls.py
git checkout HEAD~1 -- config/settings.py
python manage.py runserver
```

2. **Frontend Rollback:**

```bash
git checkout HEAD~1 -- skyfront/src/api.js
git checkout HEAD~1 -- skyfront/src/componenets/Form.jsx
git checkout HEAD~1 -- skyfront/src/componenets/ProtectedRoute.jsx
git checkout HEAD~1 -- skyfront/src/App.jsx
npm run dev
```

3. **Уведомить пользователей** о временной проблеме

## Мониторинг После Запуска

### Первые 24 часа:

- [ ] Проверять логи Django на ошибки
- [ ] Проверять Browser Console на ошибки
- [ ] Мониторить жалобы пользователей
- [ ] Следить за метриками login/logout

### Метрики для мониторинга:

- Успешные logins
- Failed logins
- Token refresh calls
- 401 errors
- CORS errors

### Индикаторы проблем:

- 🔴 Много 401 ошибок
- 🔴 Много CORS ошибок
- 🔴 Cookies не устанавливаются
- 🔴 Жалобы на "не могу войти"

## Post-Migration Tasks

### Через 1 неделю:

- [ ] Удалить fallback на Authorization header (если все OK)
- [ ] Удалить старый код localStorage (если есть остатки)
- [ ] Обновить документацию API
- [ ] Провести security audit

### Через 1 месяц:

- [ ] Проанализировать метрики безопасности
- [ ] Рассмотреть дополнительные улучшения:
  - [ ] Rate limiting для login
  - [ ] IP whitelisting
  - [ ] 2FA (Two-Factor Authentication)
  - [ ] Audit logging

## Документация

- [ ] Обновить README.md
- [ ] Обновить API документацию
- [ ] Добавить migration guide для разработчиков
- [ ] Обновить onboarding документы

## Support

### FAQ для пользователей:

**Q: Почему меня выкинуло из системы?**
A: Мы улучшили безопасность. Просто войдите заново.

**Q: Мои данные сохранились?**
A: Да, все данные в безопасности. Изменилась только система входа.

**Q: Нужно ли менять пароль?**
A: Нет, ваш пароль остался прежним.

### Контакты Support:

- Email: support@skylearn.com
- Slack: #skylearn-support
- Phone: +X-XXX-XXX-XXXX

---

## Финальная Проверка

Все чекбоксы отмечены? ✅

- [ ] Backend работает
- [ ] Frontend работает
- [ ] Login работает
- [ ] Logout работает
- [ ] Security features работают
- [ ] Документация обновлена
- [ ] Пользователи уведомлены

**Готово к запуску!** 🚀

---

**Дата:** 7 ноября 2025  
**Ответственный:** Dev Team  
**Статус:** Ready for Production
