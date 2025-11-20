# Реализация мультитенантности на уровне администраторов

## Описание
Реализована система мультитенантности на уровне администраторов для SkyLearn. Теперь каждый администратор видит и может управлять только своими данными, что позволяет одной системе обслуживать несколько независимых организаций (например, разные факультеты университета).

## Выполненные задачи

### 1. ✅ Удаление всех упоминаний Session из моделей
- Удалена модель `Session` из `core/models.py`
- Удален импорт `Session` из `accounts/views.py`
- Удалена ссылка на `SessionViewSet` из `core/urls.py`
- Обновлены тесты в `result/tests/test_views.py`

### 2. ✅ Обновление serializers для автоматического добавления admin
Добавлен метод `create()` в следующих сериализаторах для автоматической установки поля `admin`:

**core/serializers.py:**
- `NewsAndEventsSerializer`
- `SemesterSerializer`

**course/serializers.py:**
- `ProgramSerializer`
- `CourseSerializer`
- `CourseAllocationSerializer`

**accounts/serializers.py:**
- `StaffAddSerializer`
- `StudentAddSerializer`
- `ParentAddSerializer`
- `GroupSerializer`

**attendance/serializers.py:**
- `ScheduleItemSerializer`
- `AdminScheduleItemSerializer`

### 3. ✅ Обновление views для фильтрации по admin

**core/views.py:**
- `NewsAndEventsViewSet`: добавлен `get_queryset()` для фильтрации по admin
- `SemesterViewSet`: добавлен `get_queryset()` для фильтрации по admin
- `unset_current_semester()`: обновлен для работы с текущим админом

**accounts/views.py:**
- `LecturerListViewSet`: добавлен `get_queryset()` для фильтрации по admin
- `StaffCreateView`: обновлен для фильтрации по admin
- `StudentDeleteView`: добавлен `get_queryset()` для фильтрации по admin
- `StudentUpdateView`: добавлен `get_queryset()` для фильтрации по admin
- `StudentListView`: добавлен `get_queryset()` для фильтрации по admin
- `StudentDetailView`: добавлен `get_queryset()` для фильтрации по admin
- `StudentCreateView`: обновлен для фильтрации программ и групп по admin
- `GroupViewSet`: добавлен `get_queryset()` для фильтрации по admin
- `StudentsByGroupView`: добавлена проверка доступа к группе по admin

**course/views.py:**
- `ProgramListAPIView`: добавлена фильтрация программ по admin
- `ProgramDetailAPIView`: обновлен `get_object()` для проверки принадлежности админу
- `CourseListCreateAPIView`: добавлена фильтрация курсов по admin
- `CourseDetailAPIView`: обновлен `get_object()` для проверки принадлежности админу
- `CourseAllocationViewSet`: добавлен `get_queryset()` для фильтрации по admin

### 4. ✅ Обновление permissions для проверки admin

Добавлены новые классы permissions в `core/permissions.py`:

- **`IsOwnerAdmin`**: Проверяет, что объект принадлежит админу текущего пользователя
- **`CanModifyOwnData`**: Проверяет, что пользователь может изменять только свои данные (только администраторы)

### 5. ✅ Тестирование изменений

Создан тестовый скрипт `test_admin_multitenancy.py`, который проверяет:
- Создание двух независимых администраторов
- Создание данных для каждого администратора
- Изоляцию данных (каждый админ видит только свои данные)
- Проверку моделей: Programs, Groups, Semesters, Courses, News

**Результат тестирования: ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО**

## Архитектура решения

### Структура данных
Каждая модель, создаваемая администратором, имеет поле `admin`:
```python
admin = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='...',
    limit_choices_to={'is_superuser': True},
    null=True,
    blank=True
)
```

### Автоматическое заполнение admin
При создании объекта через API, поле `admin` автоматически заполняется в методе `create()` сериализатора:
```python
def create(self, validated_data):
    admin = self.context.get('admin') or self.context.get('request').user
    validated_data['admin'] = admin
    return super().create(validated_data)
```

### Фильтрация данных
Во views переопределен метод `get_queryset()` для фильтрации по admin:
```python
def get_queryset(self):
    user = self.request.user
    if user.is_superuser:
        return Model.objects.filter(admin=user)
    elif hasattr(user, 'admin') and user.admin:
        return Model.objects.filter(admin=user.admin)
    return Model.objects.none()
```

### Передача контекста
В views добавлен метод `get_serializer_context()` для передачи admin в сериализаторы:
```python
def get_serializer_context(self):
    context = super().get_serializer_context()
    context['admin'] = self.request.user if self.request.user.is_superuser else getattr(self.request.user, 'admin', None)
    return context
```

## Затронутые модели

✅ **accounts:**
- User (добавлено поле admin)
- Student (добавлено поле admin)
- Parent (добавлено поле admin)
- Group (добавлено поле admin)

✅ **course:**
- Program (добавлено поле admin)
- Course (добавлено поле admin)
- CourseAllocation (добавлено поле admin)

✅ **core:**
- NewsAndEvents (добавлено поле admin)
- Semester (добавлено поле admin)

✅ **attendance:**
- ScheduleItem (добавлено поле admin)

✅ **result:**
- Grade_1st_module (добавлено поле admin)
- Grade_2nd_module (добавлено поле admin)
- Grade_semester (добавлено поле admin)

## Миграции

Созданы и применены миграции для всех моделей:
- `accounts/migrations/0002_...`
- `course/migrations/0009_...`
- `core/migrations/0005_...`
- `attendance/migrations/...`
- `result/migrations/...`

## Безопасность

1. **Изоляция данных**: Каждый администратор видит только свои данные
2. **Автоматическое назначение**: При создании объектов admin назначается автоматически
3. **Проверка доступа**: Permissions проверяют принадлежность объектов админу
4. **Каскадное удаление**: При удалении админа удаляются все его данные

## Использование

### Для администратора:
1. Администратор создает данные через API
2. Поле `admin` автоматически заполняется
3. При запросе данных видит только свои объекты

### Для преподавателей и студентов:
1. Видят данные своего администратора (через поле `user.admin`)
2. Не могут создавать новые объекты (только админы)
3. Могут просматривать доступные им данные

## Примеры запросов API

### Создание программы (admin1):
```bash
POST /api/programs/
Authorization: Bearer <token_admin1>
{
  "title": "Computer Science",
  "summary": "CS Program"
}
```
→ Автоматически устанавливается `admin=admin1`

### Получение списка программ (admin1):
```bash
GET /api/programs/
Authorization: Bearer <token_admin1>
```
→ Возвращает только программы, где `admin=admin1`

### Получение списка программ (admin2):
```bash
GET /api/programs/
Authorization: Bearer <token_admin2>
```
→ Возвращает только программы, где `admin=admin2`

## Заключение

✅ Реализована полная мультитенантность на уровне администраторов
✅ Каждый администратор имеет изолированное пространство данных
✅ Автоматическое управление принадлежностью данных
✅ Безопасная фильтрация и проверка доступа
✅ Все тесты пройдены успешно

Система готова к использованию несколькими независимыми организациями!
