# Исправление ошибки 404 для bulk-update endpoint

## Проблема

При отправке POST запроса на `/result/api/lecturer/bulk-grades/bulk-update/` возникала ошибка 404 Not Found:

```
Not Found: /result/api/lecturer/bulk-grades/bulk-update/
[30/Oct/2025 02:23:58] "POST /result/api/lecturer/bulk-grades/bulk-update/ HTTP/1.1" 404 16613
```

## Причина

В `result/views.py` у декоратора `@action` для метода `bulk_update` отсутствовал параметр `url_path='bulk-update'`.

Django REST Framework по умолчанию генерирует URL на основе имени метода. Имя метода `bulk_update` (с подчеркиванием) автоматически преобразуется в URL, но не всегда с дефисами.

## Решение

Добавлен параметр `url_path='bulk-update'` в декоратор `@action`:

**До:**

```python
@action(detail=False, methods=['post'])
def bulk_update(self, request):
    ...
```

**После:**

```python
@action(detail=False, methods=['post'], url_path='bulk-update')
def bulk_update(self, request):
    ...
```

### Измененные файлы

- `result/views.py` - добавлен `url_path='bulk-update'` для метода `bulk_update` (строка ~275)
- `result/views.py` - добавлен `url_path='course-grades'` для метода `course_grades` (для единообразия)

## Проверка

### 1. Проверка регистрации URL

```bash
python test_bulk_update_url.py
```

Результат:

```
✅ URL найден: /result/api/lecturer/bulk-grades/bulk-update/
   View: LecturerBulkGradesViewSet
   Actions: {'post': 'bulk_update'}
```

### 2. Тесты

Запуск всех тестов для bulk_update:

```bash
python manage.py test result.tests.test_views -k bulk_update -v 2
```

Результат: **9/9 тестов прошли успешно ✅**

## Правильный URL

```
POST /result/api/lecturer/bulk-grades/bulk-update/
```

**⚠️ Важно:** URL с **дефисами** (`bulk-update`), не с подчеркиваниями (`bulk_update`)

## Пример запроса

```bash
curl -X POST http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "course_id": 1,
    "grade_type": "1st_module",
    "grades": [
      {
        "student_id": 1,
        "attendance": 25.0,
        "activities": 30.0,
        "exam": 35.0
      }
    ]
  }'
```

## Структура запроса

```json
{
  "course_id": 1, // ID курса (обязательно)
  "grade_type": "1st_module", // Тип оценки: "1st_module", "2nd_module", "semester" (обязательно)
  "grades": [
    // Массив оценок (обязательно)
    {
      "student_id": 1, // ID студента (обязательно)
      "attendance": 25.0, // Посещаемость 0-30 (необязательно)
      "activities": 30.0, // Активности 0-30 (необязательно)
      "exam": 35.0 // Экзамен 0-40 (необязательно)
    }
  ]
}
```

## Структура ответа

### Успешный ответ (200 OK)

```json
{
  "detail": "Successfully updated 2 grades",
  "updated_grades": [
    {
      "student_id": 1,
      "student_name": "John Doe",
      "attendance": 25.0,
      "activities": 30.0,
      "exam": 35.0,
      "total": 90.0
    }
  ]
}
```

### Ошибки

- **401 Unauthorized** - Пользователь не авторизован
- **403 Forbidden** - Только преподаватели могут обновлять оценки
- **400 Bad Request** - Неверные данные (отсутствуют обязательные поля, неверный grade_type)
- **404 Not Found** - Запись оценки не найдена для одного из студентов

## Примечания

1. Только авторизованные преподаватели могут использовать этот endpoint
2. Преподаватель может обновлять только оценки своих курсов
3. Все оценки обновляются в транзакции (все или ничего)
4. Поле `total` пересчитывается автоматически: `total = attendance + activities + exam`
5. Можно обновлять только некоторые поля, остальные останутся без изменений
