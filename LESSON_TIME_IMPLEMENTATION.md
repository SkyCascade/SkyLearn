# Обновление системы расписания - LessonTime

## Описание изменений

Добавлена новая модель `LessonTime` для управления типовыми временами уроков и обновлена модель `ScheduleItem` для автоматического определения времени начала и окончания занятий.

## Проблема

Раньше при создании расписания нужно было каждый раз вручную указывать время начала (`start`) и окончания (`end`) урока. В университетах обычно время уроков стандартизировано:
- 1-й урок: 9:00 - 10:30
- 2-й урок: 10:40 - 12:10
- 3-й урок: 12:40 - 14:10
- и т.д.

## Решение

### 1. Новая модель `LessonTime`

Модель для хранения типовых времен уроков:

```python
class LessonTime(models.Model):
    order = models.IntegerField(unique=True)  # Номер урока
    start_time = models.TimeField()  # Время начала
    end_time = models.TimeField()  # Время окончания
    admin = models.ForeignKey(User, ...)  # Для мультитенантности
```

**Особенности:**
- Каждый администратор может настроить свои времена уроков
- Уникальная комбинация `(order, admin)` - у каждого админа свой набор уроков
- Автоматическая сортировка по номеру урока

### 2. Обновленная модель `ScheduleItem`

Добавлены новые поля:

```python
class ScheduleItem(models.Model):
    lesson_time = models.ForeignKey(LessonTime, ...)  # Ссылка на время урока
    date = models.DateField()  # Дата проведения урока
    
    # Устаревшие поля (для обратной совместимости)
    order = models.IntegerField(null=True, blank=True)
    start = models.TimeField(null=True, blank=True)
    end = models.TimeField(null=True, blank=True)
```

**Свойства для получения времени:**
- `start_time` - автоматически получает время из `lesson_time.start_time`
- `end_time` - автоматически получает время из `lesson_time.end_time`
- `lesson_order` - автоматически получает номер урока из `lesson_time.order`

## Использование

### API endpoints

#### 1. Управление временами уроков

**GET** `/api/attendance/lesson-times/` - получить список времен уроков
```json
[
  {
    "id": 1,
    "order": 1,
    "start_time": "09:00:00",
    "end_time": "10:30:00"
  },
  {
    "id": 2,
    "order": 2,
    "start_time": "10:40:00",
    "end_time": "12:10:00"
  }
]
```

**POST** `/api/attendance/lesson-times/` - создать новое время урока
```json
{
  "order": 1,
  "start_time": "09:00",
  "end_time": "10:30"
}
```

#### 2. Создание расписания

**Старый способ (все еще работает):**
```json
{
  "course": 1,
  "group": 1,
  "day": "Monday",
  "order": 1,
  "start": "09:00",
  "end": "10:30"
}
```

**Новый способ (рекомендуется):**
```json
{
  "course": 1,
  "group": 1,
  "day": "Monday",
  "date": "2025-11-25",
  "lesson_time": 1
}
```

При новом способе:
- Не нужно указывать `start` и `end` - они автоматически подтянутся из `lesson_time`
- Не нужно указывать `order` - номер урока берется из `lesson_time`
- Обязательно указывается `date` - дата проведения занятия

### Ответ API для расписания

```json
{
  "id": 1,
  "course": 1,
  "course_title": "Python Programming",
  "course_code": "CS101",
  "group": 1,
  "group_name": "CS-101",
  "lesson_time": 1,
  "lesson_order": 1,
  "day": "Monday",
  "date": "2025-11-25",
  "start_time": "09:00:00",
  "end_time": "10:30:00"
}
```

## Преимущества

### 1. Централизованное управление
- Администратор настраивает времена уроков один раз
- Все расписания автоматически используют эти настройки
- При изменении времени урока - обновляются все связанные расписания

### 2. Упрощение создания расписания
- Не нужно каждый раз вводить время вручную
- Достаточно выбрать номер урока из списка
- Меньше ошибок при вводе времени

### 3. Консистентность данных
- Все уроки с одним номером имеют одинаковое время
- Невозможно случайно создать расписание с неправильным временем

### 4. Мультитенантность
- Каждый администратор может настроить свои времена уроков
- Разные факультеты могут иметь разное расписание звонков

## Миграция данных

Старые поля `order`, `start`, `end` в `ScheduleItem` сделаны nullable для обратной совместимости:
- Существующие расписания продолжат работать
- Новые расписания используют `lesson_time`
- Постепенно можно мигрировать старые данные

### Скрипт миграции (пример)

```python
from attendance.models import ScheduleItem, LessonTime

# Для каждого старого расписания
for schedule in ScheduleItem.objects.filter(lesson_time__isnull=True):
    # Найти или создать соответствующий LessonTime
    lesson_time, created = LessonTime.objects.get_or_create(
        order=schedule.order,
        admin=schedule.admin,
        defaults={
            'start_time': schedule.start,
            'end_time': schedule.end
        }
    )
    
    # Связать с расписанием
    schedule.lesson_time = lesson_time
    schedule.save()
```

## Обновленные сериализаторы

### LessonTimeSerializer
- Создание и управление временами уроков
- Автоматическое назначение admin

### ScheduleItemSerializer (обновлен)
- Добавлено поле `lesson_time`
- Добавлено поле `date`
- Read-only поля: `lesson_order`, `start_time`, `end_time`
- Автоматически вычисляются из связанного `lesson_time`

### AttendanceSerializer (обновлен)
- Добавлено поле `schedule_date`
- `schedule_time` вычисляется из `lesson_time`

## Примеры использования

### 1. Настройка времен уроков (один раз)

```python
# Создать стандартные времена для университета
lesson_times = [
    {'order': 1, 'start_time': '09:00', 'end_time': '10:30'},
    {'order': 2, 'start_time': '10:40', 'end_time': '12:10'},
    {'order': 3, 'start_time': '12:40', 'end_time': '14:10'},
    {'order': 4, 'start_time': '14:20', 'end_time': '15:50'},
]

for data in lesson_times:
    LessonTime.objects.create(**data, admin=admin_user)
```

### 2. Создание расписания на неделю

```python
from datetime import date, timedelta

# Понедельник, первый урок
ScheduleItem.objects.create(
    course=python_course,
    group=cs_group,
    lesson_time=lesson_time_1,  # 09:00-10:30
    day='Monday',
    date=date(2025, 11, 25),
    admin=admin_user
)

# Среда, третий урок
ScheduleItem.objects.create(
    course=python_course,
    group=cs_group,
    lesson_time=lesson_time_3,  # 12:40-14:10
    day='Wednesday',
    date=date(2025, 11, 27),
    admin=admin_user
)
```

## Тестирование

Создан тестовый скрипт `test_lesson_times.py`:

```bash
python test_lesson_times.py
```

**Результат:** ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!

## Заключение

✅ Добавлена модель `LessonTime` для управления временами уроков
✅ Обновлена модель `ScheduleItem` с поддержкой `lesson_time` и `date`
✅ Сохранена обратная совместимость со старыми полями
✅ Обновлены все сериализаторы
✅ Добавлен ViewSet для управления временами уроков
✅ Реализована мультитенантность
✅ Все тесты пройдены успешно

Теперь создание расписания стало проще и консистентнее! 🎉
