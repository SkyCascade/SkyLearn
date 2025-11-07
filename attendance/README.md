# Модуль Attendance (Посещаемость и Расписание)

## Описание

Модуль для управления расписанием занятий и учета посещаемости студентов в системе SkyLearn.

## Модели

### ScheduleItem (Расписание занятий)

- `course` - связь с курсом
- `group` - связь с группой студентов
- `order` - порядковый номер занятия в день
- `day` - день недели (Monday-Friday)
- `start` - время начала
- `end` - время окончания

### Attendance (Посещаемость)

- `Student` - связь со студентом
- `status` - статус посещения (True - присутствовал, False - отсутствовал)
- `shcedule` - связь с занятием по расписанию

## Функциональность

### Для студентов:

- Просмотр своего расписания
- Просмотр своей посещаемости
- Статистика личной посещаемости

### Для преподавателей:

- Просмотр расписания своих занятий
- Отметка посещаемости студентов на своих занятиях
- Массовое обновление посещаемости
- Статистика посещаемости по своим курсам

### Для администраторов:

- Полное управление расписанием (создание, редактирование, удаление)
- Полное управление посещаемостью
- Общая статистика по системе

## API Endpoints

### Расписание

- `GET /attendance/schedules/` - список расписания
- `GET /attendance/schedules/{id}/` - конкретное занятие
- `POST /attendance/schedules/` - создать занятие (admin/lecturer)
- `PUT/PATCH /attendance/schedules/{id}/` - обновить занятие (admin/lecturer)
- `DELETE /attendance/schedules/{id}/` - удалить занятие (admin/lecturer)
- `GET /attendance/schedules/group/{group_id}/` - расписание группы
- `GET /attendance/schedules/day/{day}/` - расписание на день
- `GET /attendance/schedules/my_schedule/` - мое расписание

### Посещаемость

- `GET /attendance/attendances/` - список посещаемости
- `GET /attendance/attendances/{id}/` - конкретная запись
- `POST /attendance/attendances/` - создать запись (admin)
- `PUT/PATCH /attendance/attendances/{id}/` - обновить запись (admin/lecturer)
- `DELETE /attendance/attendances/{id}/` - удалить запись (admin)
- `GET /attendance/attendances/schedule/{schedule_id}/` - посещаемость занятия
- `GET /attendance/attendances/student/{student_id}/` - посещаемость студента
- `GET /attendance/attendances/my_attendance/` - моя посещаемость (student)
- `GET /attendance/attendances/statistics/` - статистика
- `POST /attendance/attendances/bulk_update/` - массовое обновление (lecturer/admin)

## Установка

1. Убедитесь, что модуль добавлен в `INSTALLED_APPS` в `config/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'attendance',
    ...
]
```

2. Выполните миграции:

```bash
python manage.py makemigrations attendance
python manage.py migrate attendance
```

3. URL уже подключен в `config/urls.py`:

```python
path("attendance/", include("attendance.urls")),
```

## Использование

Подробную документацию по API см. в [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Примеры запросов

### Получить свое расписание (студент):

```bash
curl -X GET http://localhost:8000/attendance/schedules/my_schedule/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Отметить посещаемость (преподаватель):

```bash
curl -X POST http://localhost:8000/attendance/attendances/bulk_update/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_id": 1,
    "attendances": [
      {"student_id": 1, "status": true},
      {"student_id": 2, "status": false}
    ]
  }'
```

### Получить статистику:

```bash
curl -X GET http://localhost:8000/attendance/attendances/statistics/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Известные проблемы

- В модели `Attendance` поле названо `shcedule` вместо `schedule` (опечатка). Рекомендуется исправить в будущих миграциях.
- Поле `Student` в модели `Attendance` должно быть lowercase `student` по PEP8.

## Зависимости

- Django REST Framework
- django-filter
- drf-spectacular (для документации API)

## Лицензия

Часть проекта SkyLearn
