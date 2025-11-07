# Change Password Feature - Guide

## Обзор

Функциональность смены пароля реализована для всех типов пользователей:

- 👨‍🎓 Студенты (Students)
- 👨‍🏫 Преподаватели (Teachers/Lecturers)
- 👨‍💼 Администраторы (Admins)

## Backend API

### Endpoint

```
POST /accounts/change-password/
```

### Аутентификация

Требуется JWT токен в заголовке:

```
Authorization: Bearer <access_token>
```

### Request Body

```json
{
  "old_password": "текущий_пароль",
  "new_password": "новый_пароль",
  "confirm_password": "новый_пароль"
}
```

### Response

**Success (200 OK):**

```json
{
  "message": "Password changed successfully",
  "detail": "Your password has been updated. You remain logged in."
}
```

**Error (400 Bad Request):**

```json
{
  "old_password": ["Old password is incorrect."]
}
```

или

```json
{
  "confirm_password": ["New passwords do not match."]
}
```

или

```json
{
  "new_password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is too common."
  ]
}
```

### Валидация пароля

Backend использует встроенные валидаторы Django:

- Минимум 8 символов
- Не может быть слишком похожим на другую личную информацию
- Не должен быть в списке часто используемых паролей
- Не может состоять только из цифр

### Особенности реализации

1. **Проверка старого пароля**: Система проверяет, что введенный старый пароль правильный
2. **Сохранение сессии**: После смены пароля пользователь остается залогиненным (используется `update_session_auth_hash`)
3. **Универсальность**: Один endpoint для всех типов пользователей
4. **Безопасность**: Пароли хешируются с использованием Django's PBKDF2 алгоритма

## Frontend Integration

### Компонент

Создан универсальный компонент `ChangePassword.jsx` в папке `/skyfront/src/componenets/`

### Маршрут

```
/change-password
```

Доступен для всех аутентифицированных пользователей.

### Особенности UI

1. **Показ/скрытие пароля**: Кнопки для переключения видимости каждого поля
2. **Индикатор силы пароля**:

   - Very Weak (красный)
   - Weak (оранжевый)
   - Fair (желтый)
   - Good (синий)
   - Strong (зеленый)
   - Very Strong (изумрудный)

3. **Подсказки по требованиям**:

   - Минимум 8 символов
   - Заглавные и строчные буквы
   - Минимум одна цифра
   - Минимум один специальный символ

4. **Проверка совпадения**: Мгновенная проверка, что новый пароль и подтверждение совпадают

5. **Советы по безопасности**: Список лучших практик для пароля

### Интеграция в профили

#### Студент (`/pages/users/student.jsx`)

Кнопка смены пароля добавлена в секцию "Quick Actions" после кнопок посещаемости и расписания.

#### Преподаватель (`/pages/users/teacher.jsx`)

Кнопка добавлена в секцию "Quick Actions" перед списком курсов.

#### Администратор (`/pages/users/admin.jsx`)

Добавлена отдельная секция "Security Settings" с кнопкой смены пароля.

## Тестирование

### Backend

```bash
# Запустить сервер
python manage.py runserver

# Тест с curl
curl -X POST http://localhost:8000/accounts/change-password/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "старый_пароль",
    "new_password": "НовыйПароль123!",
    "confirm_password": "НовыйПароль123!"
  }'
```

### Frontend

1. Залогиньтесь как студент/учитель/админ
2. Найдите кнопку "Change Password" на дашборде
3. Заполните форму:
   - Введите текущий пароль
   - Введите новый пароль (следуя требованиям)
   - Подтвердите новый пароль
4. Нажмите "Change Password"
5. Проверьте, что появилось сообщение об успехе
6. Попробуйте залогиниться с новым паролем

### Сценарии тестирования

✅ **Успешная смена пароля**

- Правильный старый пароль
- Новый пароль соответствует требованиям
- Пароли совпадают

❌ **Неправильный старый пароль**

- Должна появиться ошибка "Old password is incorrect"

❌ **Слабый пароль**

- Должны появиться ошибки валидации

❌ **Пароли не совпадают**

- Должна появиться ошибка "New passwords do not match"

## Файлы, измененные/созданные

### Backend

1. `/accounts/serializers.py` - добавлен `ChangePasswordSerializer`
2. `/accounts/views.py` - добавлен `ChangePasswordView`
3. `/accounts/urls.py` - добавлен маршрут `change-password/`

### Frontend

1. `/skyfront/src/componenets/ChangePassword.jsx` - новый компонент
2. `/skyfront/src/App.jsx` - добавлен маршрут `/change-password`
3. `/skyfront/src/pages/users/student.jsx` - добавлена кнопка
4. `/skyfront/src/pages/users/teacher.jsx` - добавлена кнопка
5. `/skyfront/src/pages/users/admin.jsx` - добавлена секция с кнопкой

## API Documentation (drf-spectacular)

Endpoint автоматически документируется с помощью `@extend_schema` декоратора.

Доступно в Swagger UI:

```
http://localhost:8000/api/schema/swagger-ui/
```

## Безопасность

1. ✅ Требуется аутентификация (JWT)
2. ✅ Проверка старого пароля
3. ✅ Валидация нового пароля
4. ✅ Хеширование паролей
5. ✅ Сохранение сессии после смены
6. ✅ HTTPS рекомендуется в продакшене

## Возможные улучшения

1. 📧 Email уведомление о смене пароля
2. 📱 SMS верификация для критических изменений
3. 🔐 Двухфакторная аутентификация (2FA)
4. 📊 История смены паролей
5. ⏰ Принудительная смена пароля каждые N месяцев
6. 🚫 Предотвращение повторного использования старых паролей

## Поддержка

При возникновении проблем проверьте:

1. JWT токен актуален
2. Backend сервер запущен
3. Frontend правильно настроен для API запросов
4. Пользователь аутентифицирован
5. Логи сервера на наличие ошибок

---

**Дата создания**: 7 ноября 2025  
**Версия**: 1.0  
**Автор**: SkyLearn Team
