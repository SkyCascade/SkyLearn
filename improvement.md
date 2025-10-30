# 📊 SkyLearn: Комплексный план улучшений системы

> **Дата анализа:** 30 октября 2025  
> **Версия:** 1.0  
> **Основа:** Анализ текущей системы + Практика университетов Кыргызстана

---

## 📋 Содержание

1. [Критические улучшения системы оценок](#1-критические-улучшения-системы-оценок)
2. [Улучшения логики и связей](#2-улучшения-логики-и-связей)
3. [Улучшения UX/UI и производительности](#3-улучшения-ux-ui-и-производительности)
4. [Академические улучшения (специфика КР)](#4-академические-улучшения-специфика-кр)
5. [Системные улучшения безопасности](#5-системные-улучшения-безопасности)
6. [Аналитика и отчётность](#6-аналитика-и-отчётность)
7. [Интеграции и автоматизация](#7-интеграции-и-автоматизация)

---

## 1. 🔴 Критические улучшения системы оценок

### 1.1 Проблема: Дублирование моделей оценок

**Текущая ситуация:**
```python
# result/models.py
class TakenCourse(models.Model)  # Старая система оценок
class Grade_1st_module(models.Model)  # Новая система (1-й модуль)
class Grade_2nd_module(models.Model)  # Новая система (2-й модуль)
class Grade_semester(models.Model)    # Новая система (семестр)
```

**Проблемы:**
- ❌ 4 разные модели для одной и той же цели
- ❌ Нет единого источника правды (single source of truth)
- ❌ Сложность в миграции данных
- ❌ Противоречивые данные между моделями

**Улучшение:**
```python
class Grade(models.Model):
    """Единая модель оценок с типизацией периода"""
    PERIOD_CHOICES = [
        ('1st_module', 'First Module'),
        ('2nd_module', 'Second Module'),
        ('semester', 'Semester'),
        ('final', 'Final Grade'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    
    # Компоненты оценки (0-100 баллов)
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    activities = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exam = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    
    # Буквенная оценка (автоматически)
    letter_grade = models.CharField(max_length=2, editable=False, blank=True)
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course', 'period')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'course', 'period']),
            models.Index(fields=['course', 'period']),
        ]
    
    def save(self, *args, **kwargs):
        # Автоматический расчет total и letter_grade
        self.total = self.attendance + self.activities + self.exam
        self.letter_grade = self.calculate_letter_grade()
        super().save(*args, **kwargs)
    
    def calculate_letter_grade(self):
        """Расчет буквенной оценки по шкале университетов КР"""
        if self.total >= 95: return 'A+'
        elif self.total >= 90: return 'A'
        elif self.total >= 85: return 'A-'
        # ... и т.д.
```

**Преимущества:**
- ✅ Единая точка входа для всех оценок
- ✅ Легкая миграция и консистентность
- ✅ Простота в расширении (добавить новый период = 1 строка)
- ✅ Оптимизированные запросы с индексами

---

### 1.2 Проблема: Отсутствие валидации весов компонентов

**Текущая ситуация:**
```python
# В моделях нет проверки, что attendance + activities + exam = 100
attendance = models.DecimalField(max_digits=5, decimal_places=2)
activities = models.DecimalField(max_digits=5, decimal_places=2)
exam = models.DecimalField(max_digits=5, decimal_places=2)
```

**Проблемы:**
- ❌ Преподаватель может поставить attendance=40, activities=40, exam=50 (total=130!)
- ❌ Нет конфигурации весов на уровне курса
- ❌ Все курсы используют одинаковые веса (30/30/40)

**Улучшение:**
```python
class Course(models.Model):
    # ...существующие поля...
    
    # Конфигурация весов (в процентах)
    attendance_weight = models.IntegerField(default=30)
    activities_weight = models.IntegerField(default=30)
    exam_weight = models.IntegerField(default=40)
    
    def clean(self):
        """Валидация весов"""
        total_weight = self.attendance_weight + self.activities_weight + self.exam_weight
        if total_weight != 100:
            raise ValidationError(
                f'Сумма весов должна быть 100%, сейчас {total_weight}%'
            )

class Grade(models.Model):
    # ...
    
    def clean(self):
        """Валидация оценок с учетом весов курса"""
        if self.attendance > self.course.attendance_weight:
            raise ValidationError(
                f'Посещаемость не может быть больше {self.course.attendance_weight}'
            )
        # ... аналогично для activities и exam
```

---

### 1.3 Проблема: Отсутствие истории изменений оценок

**Текущая ситуация:**
- ❌ Нет логирования кто и когда изменил оценку
- ❌ Невозможно откатить изменения
- ❌ Нет аудита для споров со студентами

**Улучшение:**
```python
class GradeHistory(models.Model):
    """История изменений оценок для аудита"""
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    # Старые значения
    old_attendance = models.DecimalField(max_digits=5, decimal_places=2)
    old_activities = models.DecimalField(max_digits=5, decimal_places=2)
    old_exam = models.DecimalField(max_digits=5, decimal_places=2)
    old_total = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Новые значения
    new_attendance = models.DecimalField(max_digits=5, decimal_places=2)
    new_activities = models.DecimalField(max_digits=5, decimal_places=2)
    new_exam = models.DecimalField(max_digits=5, decimal_places=2)
    new_total = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Причина изменения
    reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
```

**Применение:**
```python
# В signals или методе save()
@receiver(pre_save, sender=Grade)
def log_grade_change(sender, instance, **kwargs):
    if instance.pk:  # Если это обновление, а не создание
        old_grade = Grade.objects.get(pk=instance.pk)
        GradeHistory.objects.create(
            grade=instance,
            changed_by=get_current_user(),
            old_attendance=old_grade.attendance,
            # ... и т.д.
        )
```

---

## 2. 🔗 Улучшения логики и связей

### 2.1 Проблема: Слабая связь между Student и Group

**Текущая ситуация:**
```python
class Student(User):
    level = models.CharField(max_length=25, choices=LEVEL)
    department = models.CharField(max_length=200)
```

**Проблемы:**
- ❌ `department` - это просто строка, а не FK
- ❌ Нет формализованной модели Group
- ❌ Невозможно отследить переводы студентов между группами
- ❌ Сложно получить всех студентов группы

**Улучшение:**
```python
class Group(models.Model):
    """Учебная группа (например, CS-22, IS-23)"""
    name = models.CharField(max_length=50, unique=True)  # CS-22
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=LEVEL)
    admission_year = models.IntegerField()  # 2022
    curator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='curated_groups'
    )
    
    # Академический год и семестр
    current_semester = models.ForeignKey(
        Semester, 
        on_delete=models.SET_NULL,
        null=True
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.program})"

class GroupMembership(models.Model):
    """История принадлежности студента к группам"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    # Период членства
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Причина перевода
    REASON_CHOICES = [
        ('admission', 'Поступление'),
        ('transfer', 'Перевод'),
        ('restoration', 'Восстановление'),
        ('graduation', 'Выпуск'),
    ]
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'group', 'start_date')

class Student(User):
    # Удаляем department, level (они теперь в Group)
    
    @property
    def current_group(self):
        """Текущая группа студента"""
        membership = GroupMembership.objects.filter(
            student=self,
            is_active=True
        ).first()
        return membership.group if membership else None
```

**Преимущества:**
- ✅ Формализованная структура групп
- ✅ История переводов студентов
- ✅ Легко получить всех студентов группы
- ✅ Связь с куратором и программой

---

### 2.2 Проблема: CourseAllocation без привязки к семестру

**Текущая ситуация:**
```python
class CourseAllocation(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, related_name='allocated_course')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
```

**Проблемы:**
- ❌ Нет привязки к конкретному семестру
- ❌ Нет информации о группах, которым преподается курс
- ❌ Невозможно отследить нагрузку преподавателя
- ❌ ManyToMany с Course слишком общий

**Улучшение:**
```python
class CourseOffering(models.Model):
    """Предложение курса в конкретном семестре для группы"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'is_lecturer': True}
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Расписание
    schedule = models.JSONField(default=dict)  # {"Monday": ["10:00-11:30"], ...}
    room = models.CharField(max_length=50, blank=True)
    
    # Статус
    STATUS_CHOICES = [
        ('planned', 'Запланирован'),
        ('active', 'Активен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Даты
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Нагрузка (часы)
    lecture_hours = models.IntegerField(default=0)
    practice_hours = models.IntegerField(default=0)
    lab_hours = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('course', 'group', 'semester')
        ordering = ['-semester', 'course']
    
    def __str__(self):
        return f"{self.course} - {self.group} ({self.semester})"
    
    @property
    def total_hours(self):
        return self.lecture_hours + self.practice_hours + self.lab_hours
    
    @property
    def enrollment_count(self):
        """Количество записавшихся студентов"""
        return self.enrollments.filter(status='active').count()

class Enrollment(models.Model):
    """Запись студента на курс"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    offering = models.ForeignKey(
        CourseOffering, 
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Статус записи
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('dropped', 'Отчислен'),
        ('completed', 'Завершён'),
        ('transferred', 'Переведён'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    dropped_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'offering')
```

**Преимущества:**
- ✅ Четкая привязка: Курс → Группа → Семестр → Преподаватель
- ✅ Отслеживание нагрузки преподавателя
- ✅ История записей студентов (active/dropped)
- ✅ Расписание и аудитории

---

### 2.3 Проблема: Отсутствие Prerequisites (пререквизитов)

**Текущая ситуация:**
- ❌ Нет проверки, что студент прошел необходимые курсы
- ❌ Студент может записаться на "Algorithms II" без "Algorithms I"

**Улучшение:**
```python
class Course(models.Model):
    # ...существующие поля...
    
    # Пререквизиты
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='required_for'
    )
    
    # Минимальная оценка для пререквизита
    min_prerequisite_grade = models.CharField(
        max_length=2,
        default='D',
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    
    def can_enroll(self, student):
        """Может ли студент записаться на курс"""
        for prereq in self.prerequisites.all():
            # Проверяем, есть ли оценка по пререквизиту
            try:
                grade = Grade.objects.get(
                    student=student,
                    course=prereq,
                    period='semester'
                )
                if not self._meets_min_grade(grade.letter_grade):
                    return False, f"Требуется оценка {self.min_prerequisite_grade} по курсу {prereq}"
            except Grade.DoesNotExist:
                return False, f"Сначала необходимо завершить курс {prereq}"
        
        return True, "OK"
    
    def _meets_min_grade(self, actual_grade):
        """Проверка минимальной оценки"""
        grade_order = ['F', 'D', 'C', 'B', 'A']
        return grade_order.index(actual_grade[0]) >= grade_order.index(self.min_prerequisite_grade)
```

---

## 3. 🎨 Улучшения UX/UI и производительности

### 3.1 Проблема: N+1 запросы при загрузке оценок

**Текущая ситуация:**
```python
# В представлении
grades = Grade_1st_module.objects.filter(course=course)
for grade in grades:
    print(grade.student.name)  # N+1 запрос!
    print(grade.lecturer.name)  # Ещё один запрос!
```

**Улучшение:**
```python
# Оптимизированный запрос с select_related
grades = Grade.objects.filter(
    course=course,
    period='1st_module'
).select_related(
    'student',
    'student__user',
    'lecturer',
    'course'
).prefetch_related(
    'course__program'
)

# Или создать менеджер
class GradeManager(models.Manager):
    def with_relations(self):
        return self.select_related(
            'student', 'lecturer', 'course'
        ).prefetch_related('course__program')

class Grade(models.Model):
    objects = GradeManager()
    # ...

# Использование
grades = Grade.objects.with_relations().filter(course=course)
```

**Результат:**
- ❌ Было: 1 запрос + N запросов = 1 + 100 = 101 запрос
- ✅ Стало: 1 запрос с JOIN = 1 запрос

---

### 3.2 Проблема: Отсутствие кеширования

**Текущая ситуация:**
- ❌ Каждый раз идет запрос к БД за списком групп
- ❌ Справочники (Programs, Courses) загружаются постоянно

**Улучшение:**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# В модели
from django.core.cache import cache

class Group(models.Model):
    # ...
    
    @classmethod
    def get_active_groups(cls):
        """Кешированный список активных групп"""
        cache_key = 'active_groups'
        groups = cache.get(cache_key)
        
        if groups is None:
            groups = list(cls.objects.filter(is_active=True).select_related('program'))
            cache.set(cache_key, groups, 3600)  # 1 час
        
        return groups
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Инвалидация кеша
        cache.delete('active_groups')

# В views
def get_groups(request):
    groups = Group.get_active_groups()  # Из кеша!
```

---

### 3.3 Проблема: Нет real-time уведомлений

**Текущая ситуация:**
- ❌ Студент не знает, что преподаватель выставил оценки
- ❌ Преподаватель не получает уведомление о новом студенте

**Улучшение:**
```python
# Добавить модель Notification
class Notification(models.Model):
    TYPE_CHOICES = [
        ('grade_posted', 'Оценка выставлена'),
        ('course_enrollment', 'Запись на курс'),
        ('grade_changed', 'Оценка изменена'),
        ('deadline', 'Приближается дедлайн'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# В signals
@receiver(post_save, sender=Grade)
def notify_grade_posted(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.student.user,
            type='grade_posted',
            title='Новая оценка',
            message=f'Преподаватель {instance.lecturer} выставил оценку по курсу {instance.course}',
            link=f'/grades/{instance.id}/'
        )

# WebSocket для real-time (с Django Channels)
# consumers.py
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        await self.channel_layer.group_add(
            f'user_{self.user_id}',
            self.channel_name
        )
        await self.accept()
    
    async def notification_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
```

---

## 4. 🎓 Академические улучшения (специфика КР)

### 4.1 Система академической задолженности

**В университетах КР:**
- Студент может иметь академическую задолженность (долги)
- Разрешено не более 2-3 долгов для перехода на следующий курс
- Есть пересдачи (ресит)

**Улучшение:**
```python
class AcademicDebt(models.Model):
    """Академическая задолженность"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Тип задолженности
    TYPE_CHOICES = [
        ('failed_exam', 'Не сдал экзамен'),
        ('failed_course', 'Не прошел курс'),
        ('attendance', 'Низкая посещаемость'),
        ('not_submitted', 'Не сдал задания'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Статус
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('resolved', 'Закрыта'),
        ('pending_retake', 'Ожидает пересдачи'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Пересдача
    retake_scheduled = models.DateTimeField(null=True, blank=True)
    retake_attempts = models.IntegerField(default=0)
    max_retake_attempts = models.IntegerField(default=3)
    
    class Meta:
        unique_together = ('student', 'course', 'semester')

class Student(User):
    # ...
    
    def can_progress_to_next_year(self):
        """Может ли студент перейти на следующий курс"""
        active_debts = AcademicDebt.objects.filter(
            student=self,
            status='active'
        ).count()
        
        # Правило: не более 2 долгов
        return active_debts <= 2
    
    @property
    def academic_status(self):
        """Академический статус"""
        debt_count = AcademicDebt.objects.filter(
            student=self,
            status='active'
        ).count()
        
        if debt_count == 0:
            return 'excellent'
        elif debt_count <= 2:
            return 'warning'
        else:
            return 'critical'
```

---

### 4.2 ГОСТы и стандарты КР

**В университетах КР:**
- Обязательны государственные стандарты (ГОСы)
- Определенное количество кредитов по категориям
- Обязательные дисциплины (государственный компонент)

**Улучшение:**
```python
class Course(models.Model):
    # ...существующие поля...
    
    # Классификация по ГОСу
    CATEGORY_CHOICES = [
        ('general', 'Общеобразовательный'),
        ('core', 'Базовый (государственный компонент)'),
        ('major', 'Профилирующий'),
        ('elective', 'Элективный'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Кредиты (ECTS)
    credits = models.IntegerField()
    
    # Обязательность
    is_mandatory = models.BooleanField(default=False)
    
    # Язык преподавания
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('ky', 'Кыргызский'),
        ('en', 'Английский'),
    ]
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ru')

class Program(models.Model):
    # ...
    
    # Требования ГОСа
    min_total_credits = models.IntegerField(default=240)  # Для бакалавра
    min_core_credits = models.IntegerField(default=60)
    min_major_credits = models.IntegerField(default=120)
    min_elective_credits = models.IntegerField(default=60)
    
    def validate_curriculum(self):
        """Проверка соответствия ГОСу"""
        courses = Course.objects.filter(program=self)
        
        total_credits = courses.aggregate(Sum('credits'))['credits__sum'] or 0
        core_credits = courses.filter(category='core').aggregate(Sum('credits'))['credits__sum'] or 0
        major_credits = courses.filter(category='major').aggregate(Sum('credits'))['credits__sum'] or 0
        elective_credits = courses.filter(category='elective').aggregate(Sum('credits'))['credits__sum'] or 0
        
        errors = []
        if total_credits < self.min_total_credits:
            errors.append(f'Недостаточно кредитов: {total_credits}/{self.min_total_credits}')
        if core_credits < self.min_core_credits:
            errors.append(f'Недостаточно базовых кредитов: {core_credits}/{self.min_core_credits}')
        
        return len(errors) == 0, errors
```

---

### 4.3 Стипендии и академическая успеваемость

**В университетах КР:**
- Стипендия зависит от среднего балла (GPA)
- Социальные стипендии
- Гранты

**Улучшение:**
```python
class Scholarship(models.Model):
    """Стипендия"""
    TYPE_CHOICES = [
        ('academic', 'Академическая'),
        ('social', 'Социальная'),
        ('grant', 'Грант'),
        ('presidential', 'Президентская'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Критерии
    min_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    max_debts = models.IntegerField(default=0)
    requires_social_status = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)

class ScholarshipRecipient(models.Model):
    """Получатель стипендии"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Статус
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('suspended', 'Приостановлена'),
        ('revoked', 'Отменена'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Даты
    granted_at = models.DateField()
    expires_at = models.DateField(null=True, blank=True)
    
    # GPA на момент назначения
    gpa_at_grant = models.DecimalField(max_digits=3, decimal_places=2)

class Student(User):
    # ...
    
    def calculate_gpa(self, semester=None):
        """Расчет GPA (Grade Point Average)"""
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.67,
            'B+': 3.33, 'B': 3.0, 'B-': 2.67,
            'C+': 2.33, 'C': 2.0, 'C-': 1.67,
            'D+': 1.33, 'D': 1.0, 'F': 0.0
        }
        
        grades_query = Grade.objects.filter(student=self, period='semester')
        if semester:
            grades_query = grades_query.filter(course__semester=semester)
        
        grades = grades_query.select_related('course')
        
        total_points = 0
        total_credits = 0
        
        for grade in grades:
            points = grade_points.get(grade.letter_grade, 0)
            credits = grade.course.credits
            total_points += points * credits
            total_credits += credits
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    
    def is_eligible_for_scholarship(self, scholarship):
        """Проверка права на стипендию"""
        gpa = self.calculate_gpa()
        debt_count = AcademicDebt.objects.filter(student=self, status='active').count()
        
        if gpa < scholarship.min_gpa:
            return False, f'Недостаточный GPA: {gpa} < {scholarship.min_gpa}'
        
        if debt_count > scholarship.max_debts:
            return False, f'Слишком много долгов: {debt_count} > {scholarship.max_debts}'
        
        return True, 'Соответствует критериям'
```

---

## 5. 🔒 Системные улучшения безопасности

### 5.1 Проблема: Слабая система прав доступа

**Текущая ситуация:**
```python
# Только декораторы @lecturer_required, @student_required
# Нет гранулярного контроля доступа
```

**Улучшение:**
```python
# Использование django-guardian для object-level permissions
from guardian.shortcuts import assign_perm, get_objects_for_user

class CourseOffering(models.Model):
    # ...
    
    class Meta:
        permissions = [
            ('view_grades', 'Can view grades'),
            ('edit_grades', 'Can edit grades'),
            ('approve_grades', 'Can approve grades'),
        ]

# При создании CourseOffering
def create_course_offering(lecturer, course, group):
    offering = CourseOffering.objects.create(
        lecturer=lecturer,
        course=course,
        group=group
    )
    
    # Назначаем права преподавателю
    assign_perm('view_grades', lecturer, offering)
    assign_perm('edit_grades', lecturer, offering)
    
    # Права студентам
    for student in group.students.all():
        assign_perm('view_grades', student.user, offering)
    
    return offering

# В представлении
def edit_grades(request, offering_id):
    offering = get_object_or_404(CourseOffering, id=offering_id)
    
    # Проверка прав
    if not request.user.has_perm('edit_grades', offering):
        return HttpResponseForbidden()
    
    # ...
```

---

### 5.2 Проблема: Нет защиты от мошенничества с оценками

**Улучшение:**
```python
class GradeApproval(models.Model):
    """Система одобрения оценок"""
    grade = models.OneToOneField(Grade, on_delete=models.CASCADE)
    
    # Кто выставил
    submitted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_grades'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Кто проверил (зав. кафедрой)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_grades'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Статус
    STATUS_CHOICES = [
        ('pending', 'Ожидает проверки'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Комментарий при отклонении
    rejection_reason = models.TextField(blank=True)
    
    # Цифровая подпись (для защиты)
    digital_signature = models.CharField(max_length=256, blank=True)
    
    def generate_signature(self):
        """Генерация цифровой подписи"""
        import hashlib
        data = f"{self.grade.id}{self.submitted_by.id}{self.submitted_at}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        if not self.digital_signature:
            self.digital_signature = self.generate_signature()
        super().save(*args, **kwargs)

# Настройка workflow
class GradeWorkflow:
    @staticmethod
    def submit_for_approval(grades, lecturer):
        """Отправка оценок на одобрение"""
        for grade in grades:
            GradeApproval.objects.create(
                grade=grade,
                submitted_by=lecturer,
                status='pending'
            )
    
    @staticmethod
    def approve_grades(grades, approver):
        """Одобрение оценок заведующим"""
        for grade in grades:
            approval = GradeApproval.objects.get(grade=grade)
            approval.approved_by = approver
            approval.approved_at = timezone.now()
            approval.status = 'approved'
            approval.save()
```

---

## 6. 📊 Аналитика и отчётность

### 6.1 Дашборд аналитики для администрации

**Улучшение:**
```python
# analytics/models.py
class AnalyticsReport(models.Model):
    """Аналитические отчёты"""
    REPORT_TYPE_CHOICES = [
        ('enrollment', 'Статистика записей'),
        ('performance', 'Успеваемость'),
        ('attendance', 'Посещаемость'),
        ('retention', 'Удержание студентов'),
        ('lecturer_load', 'Нагрузка преподавателей'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Данные
    data = models.JSONField()
    
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-generated_at']

# analytics/services.py
class AnalyticsService:
    @staticmethod
    def generate_performance_report(semester):
        """Отчёт по успеваемости"""
        grades = Grade.objects.filter(
            course__semester=semester,
            period='semester'
        )
        
        # Распределение оценок
        grade_distribution = grades.values('letter_grade').annotate(
            count=Count('id')
        )
        
        # Средний балл по программам
        avg_by_program = grades.values(
            'student__current_group__program__name'
        ).annotate(
            avg_total=Avg('total')
        )
        
        # Количество долгов
        debts = AcademicDebt.objects.filter(
            semester=semester,
            status='active'
        ).count()
        
        return {
            'grade_distribution': list(grade_distribution),
            'avg_by_program': list(avg_by_program),
            'total_debts': debts,
            'total_students': grades.values('student').distinct().count(),
        }
    
    @staticmethod
    def generate_lecturer_load_report(semester):
        """Отчёт по нагрузке преподавателей"""
        offerings = CourseOffering.objects.filter(
            semester=semester
        ).select_related('lecturer', 'course', 'group')
        
        lecturer_stats = {}
        for offering in offerings:
            lecturer_id = offering.lecturer.id
            if lecturer_id not in lecturer_stats:
                lecturer_stats[lecturer_id] = {
                    'name': offering.lecturer.get_full_name(),
                    'courses': [],
                    'total_hours': 0,
                    'total_students': 0,
                }
            
            lecturer_stats[lecturer_id]['courses'].append({
                'course': offering.course.title,
                'group': offering.group.name,
                'hours': offering.total_hours,
                'students': offering.enrollment_count,
            })
            lecturer_stats[lecturer_id]['total_hours'] += offering.total_hours
            lecturer_stats[lecturer_id]['total_students'] += offering.enrollment_count
        
        return lecturer_stats
```

---

### 6.2 Экспорт данных в различные форматы

**Улучшение:**
```python
# export/services.py
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

class ExportService:
    @staticmethod
    def export_grades_to_excel(course_offering):
        """Экспорт оценок в Excel"""
        grades = Grade.objects.filter(
            course=course_offering.course,
            period='semester'
        ).select_related('student')
        
        # Создаем DataFrame
        data = []
        for grade in grades:
            data.append({
                'ID': grade.student.id,
                'ФИО': grade.student.get_full_name(),
                'Группа': grade.student.current_group.name,
                'Посещаемость': float(grade.attendance),
                'Активность': float(grade.activities),
                'Экзамен': float(grade.exam),
                'Итого': float(grade.total),
                'Оценка': grade.letter_grade,
            })
        
        df = pd.DataFrame(data)
        
        # Создаем Excel файл с форматированием
        wb = Workbook()
        ws = wb.active
        ws.title = "Оценки"
        
        # Заголовок
        ws.append(['Ведомость оценок'])
        ws.merge_cells('A1:H1')
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        
        # Информация о курсе
        ws.append([f'Курс: {course_offering.course.title}'])
        ws.append([f'Преподаватель: {course_offering.lecturer.get_full_name()}'])
        ws.append([f'Группа: {course_offering.group.name}'])
        ws.append([])  # Пустая строка
        
        # Заголовки столбцов
        headers = list(df.columns)
        ws.append(headers)
        
        # Форматирование заголовков
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        for cell in ws[6]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Данные
        for _, row in df.iterrows():
            ws.append(row.tolist())
        
        # Автоширина столбцов
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max_length + 2
        
        return wb
    
    @staticmethod
    def export_transcript(student):
        """Экспорт транскрипта студента"""
        grades = Grade.objects.filter(
            student=student,
            period='semester'
        ).select_related('course', 'course__program').order_by('course__semester')
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Транскрипт"
        
        # Шапка
        ws.append(['АКАДЕМИЧЕСКАЯ СПРАВКА (ТРАНСКРИПТ)'])
        ws.merge_cells('A1:G1')
        ws['A1'].font = Font(size=18, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        
        ws.append([])
        ws.append([f'Студент: {student.get_full_name()}'])
        ws.append([f'ID: {student.id}'])
        ws.append([f'Программа: {student.current_group.program.title}'])
        ws.append([f'Группа: {student.current_group.name}'])
        ws.append([f'GPA: {student.calculate_gpa()}'])
        ws.append([])
        
        # Заголовки
        ws.append(['Семестр', 'Код курса', 'Название курса', 'Кредиты', 'Оценка', 'Баллы', 'Преподаватель'])
        
        # Данные по семестрам
        current_semester = None
        for grade in grades:
            semester = grade.course.semester
            if current_semester != semester:
                ws.append([])
                ws.append([f'{semester}', '', '', '', '', '', ''])
                current_semester = semester
            
            ws.append([
                '',
                grade.course.code,
                grade.course.title,
                grade.course.credits,
                grade.letter_grade,
                float(grade.total),
                grade.lecturer.get_full_name() if grade.lecturer else '-'
            ])
        
        return wb
```

---

## 7. 🔌 Интеграции и автоматизация

### 7.1 Интеграция с платёжными системами

**Для университетов КР:**
- Оплата обучения онлайн (Элсом, О!, MBank)
- Контроль оплаты перед записью на курс

**Улучшение:**
```python
# payments/models.py
class Payment(models.Model):
    """Платежи студентов"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Сумма
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KGS')
    
    # Тип платежа
    TYPE_CHOICES = [
        ('tuition', 'Оплата обучения'),
        ('dormitory', 'Общежитие'),
        ('library', 'Библиотека'),
        ('services', 'Услуги'),
    ]
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Статус
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'В обработке'),
        ('completed', 'Оплачено'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Платёжная система
    PROVIDER_CHOICES = [
        ('elsom', 'Элсом'),
        ('o', 'О!'),
        ('mbank', 'MBank'),
        ('balance', 'Balance'),
    ]
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, blank=True)
    
    # Данные транзакции
    transaction_id = models.CharField(max_length=200, unique=True, blank=True)
    provider_response = models.JSONField(default=dict)
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

class Student(User):
    # ...
    
    def has_paid_tuition(self, semester):
        """Проверка оплаты за семестр"""
        payment = Payment.objects.filter(
            student=self,
            semester=semester,
            payment_type='tuition',
            status='completed'
        ).first()
        
        return payment is not None
    
    def can_enroll(self, course_offering):
        """Может ли записаться на курс"""
        # Проверка оплаты
        if not self.has_paid_tuition(course_offering.semester):
            return False, 'Необходимо оплатить обучение'
        
        # Проверка пререквизитов
        can_enroll, reason = course_offering.course.can_enroll(self)
        if not can_enroll:
            return False, reason
        
        return True, 'OK'

# payments/services.py
class PaymentService:
    @staticmethod
    def create_payment_link(student, semester, amount):
        """Создание ссылки на оплату"""
        payment = Payment.objects.create(
            student=student,
            semester=semester,
            amount=amount,
            payment_type='tuition',
            status='pending'
        )
        
        # Генерация ссылки для Элсом (пример)
        # В реальности - интеграция с API платёжной системы
        payment_url = f"https://elsom.kg/pay?order_id={payment.id}&amount={amount}"
        
        return payment, payment_url
    
    @staticmethod
    def handle_payment_callback(transaction_id, status, provider_data):
        """Обработка callback от платёжной системы"""
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.status = 'completed' if status == 'success' else 'failed'
            payment.provider_response = provider_data
            payment.paid_at = timezone.now()
            payment.save()
            
            # Отправка уведомления студенту
            if payment.status == 'completed':
                Notification.objects.create(
                    recipient=payment.student.user,
                    type='payment_success',
                    title='Оплата принята',
                    message=f'Ваш платеж на сумму {payment.amount} KGS принят',
                )
            
            return True
        except Payment.DoesNotExist:
            return False
```

---

### 7.2 Автоматизация рассылок

**Улучшение:**
```python
# notifications/tasks.py (с Celery)
from celery import shared_task

@shared_task
def send_grade_notifications(course_offering_id):
    """Автоматическая рассылка уведомлений об оценках"""
    offering = CourseOffering.objects.get(id=course_offering_id)
    grades = Grade.objects.filter(
        course=offering.course,
        period='semester'
    ).select_related('student')
    
    for grade in grades:
        # Email
        send_mail(
            subject=f'Оценка по курсу {offering.course.title}',
            message=f'Здравствуйте, {grade.student.first_name}!\n\n'
                    f'Ваша оценка: {grade.letter_grade} ({grade.total} баллов)\n'
                    f'Преподаватель: {offering.lecturer.get_full_name()}',
            from_email='noreply@salymbekov.kg',
            recipient_list=[grade.student.email],
        )
        
        # SMS (через SMS.kg API)
        send_sms(
            phone=grade.student.phone,
            message=f'Оценка по {offering.course.code}: {grade.letter_grade}'
        )
        
        # Push-уведомление
        send_push_notification(
            user=grade.student.user,
            title='Новая оценка',
            body=f'{offering.course.title}: {grade.letter_grade}'
        )

@shared_task
def send_deadline_reminders():
    """Напоминания о приближающихся дедлайнах"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Экзамены завтра
    offerings = CourseOffering.objects.filter(
        end_date=tomorrow
    ).select_related('course', 'group')
    
    for offering in offerings:
        enrollments = Enrollment.objects.filter(
            offering=offering,
            status='active'
        ).select_related('student')
        
        for enrollment in enrollments:
            Notification.objects.create(
                recipient=enrollment.student.user,
                type='deadline',
                title='Завтра экзамен!',
                message=f'Напоминаем: завтра экзамен по курсу {offering.course.title}'
            )

@shared_task
def generate_weekly_reports():
    """Еженедельная генерация отчётов"""
    current_semester = Semester.objects.filter(is_current=True).first()
    
    # Отчёт по успеваемости
    performance_data = AnalyticsService.generate_performance_report(current_semester)
    AnalyticsReport.objects.create(
        report_type='performance',
        semester=current_semester,
        data=performance_data
    )
    
    # Отчёт по нагрузке преподавателей
    load_data = AnalyticsService.generate_lecturer_load_report(current_semester)
    AnalyticsReport.objects.create(
        report_type='lecturer_load',
        semester=current_semester,
        data=load_data
    )

# Настройка периодических задач (celery beat)
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-deadline-reminders-daily': {
        'task': 'notifications.tasks.send_deadline_reminders',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
    'generate-weekly-reports': {
        'task': 'notifications.tasks.generate_weekly_reports',
        'schedule': crontab(day_of_week='monday', hour=6, minute=0),  # Каждый понедельник в 6:00
    },
}
```

---

### 7.3 Интеграция с электронной библиотекой

**Улучшение:**
```python
# library/models.py
class LibraryResource(models.Model):
    """Ресурсы библиотеки"""
    TYPE_CHOICES = [
        ('book', 'Книга'),
        ('article', 'Статья'),
        ('thesis', 'Диссертация'),
        ('journal', 'Журнал'),
    ]
    
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Файл (PDF)
    file = models.FileField(upload_to='library/', blank=True)
    
    # Связь с курсами
    courses = models.ManyToManyField(Course, related_name='library_resources')
    
    # Доступность
    is_available_online = models.BooleanField(default=True)
    physical_copies = models.IntegerField(default=0)
    
    # Метаданные
    publisher = models.CharField(max_length=200, blank=True)
    year = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=2, default='ru')
    
    created_at = models.DateTimeField(auto_now_add=True)

class LibraryLoan(models.Model):
    """Выдача книг"""
    resource = models.ForeignKey(LibraryResource, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    # Даты
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    
    # Статус
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('returned', 'Возвращена'),
        ('overdue', 'Просрочена'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Штраф за просрочку
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def is_overdue(self):
        if self.status == 'active' and self.due_date < timezone.now().date():
            return True
        return False
    
    def calculate_fine(self):
        """Расчет штрафа (10 сом за день)"""
        if self.is_overdue:
            days_overdue = (timezone.now().date() - self.due_date).days
            self.fine_amount = days_overdue * 10
            self.status = 'overdue'
            self.save()

# Автоматическая задача для проверки просрочек
@shared_task
def check_library_overdue():
    """Проверка просроченных книг"""
    loans = LibraryLoan.objects.filter(status='active', due_date__lt=timezone.now().date())
    
    for loan in loans:
        loan.calculate_fine()
        
        # Уведомление студента
        Notification.objects.create(
            recipient=loan.student.user,
            type='library_overdue',
            title='Просрочка возврата книги',
            message=f'Книга "{loan.resource.title}" просрочена. Штраф: {loan.fine_amount} KGS'
        )
```

---

## 📊 Приоритизация улучшений

### 🔴 Критические (внедрить немедленно)

1. **Унификация моделей оценок** - устранить дублирование Grade_1st_module, Grade_2nd_module, Grade_semester
2. **История изменений оценок (GradeHistory)** - для аудита и разрешения споров
3. **Оптимизация запросов** - select_related/prefetch_related для устранения N+1

### 🟠 Высокий приоритет (1-2 месяца)

4. **Формализация групп (Group + GroupMembership)** - для корректной работы с группами
5. **Система CourseOffering + Enrollment** - замена CourseAllocation
6. **Валидация весов компонентов оценок** - предотвращение ошибок при выставлении оценок
7. **Академические задолжен// filepath: /Users/adminbaike/Desktop/projects/SkyLearn/SYSTEM_IMPROVEMENTS_PLAN.md
# 📊 SkyLearn: Комплексный план улучшений системы

> **Дата анализа:** 30 октября 2025  
> **Версия:** 1.0  
> **Основа:** Анализ текущей системы + Практика университетов Кыргызстана

---

## 📋 Содержание

1. [Критические улучшения системы оценок](#1-критические-улучшения-системы-оценок)
2. [Улучшения логики и связей](#2-улучшения-логики-и-связей)
3. [Улучшения UX/UI и производительности](#3-улучшения-ux-ui-и-производительности)
4. [Академические улучшения (специфика КР)](#4-академические-улучшения-специфика-кр)
5. [Системные улучшения безопасности](#5-системные-улучшения-безопасности)
6. [Аналитика и отчётность](#6-аналитика-и-отчётность)
7. [Интеграции и автоматизация](#7-интеграции-и-автоматизация)

---

## 1. 🔴 Критические улучшения системы оценок

### 1.1 Проблема: Дублирование моделей оценок

**Текущая ситуация:**
```python
# result/models.py
class TakenCourse(models.Model)  # Старая система оценок
class Grade_1st_module(models.Model)  # Новая система (1-й модуль)
class Grade_2nd_module(models.Model)  # Новая система (2-й модуль)
class Grade_semester(models.Model)    # Новая система (семестр)
```

**Проблемы:**
- ❌ 4 разные модели для одной и той же цели
- ❌ Нет единого источника правды (single source of truth)
- ❌ Сложность в миграции данных
- ❌ Противоречивые данные между моделями

**Улучшение:**
```python
class Grade(models.Model):
    """Единая модель оценок с типизацией периода"""
    PERIOD_CHOICES = [
        ('1st_module', 'First Module'),
        ('2nd_module', 'Second Module'),
        ('semester', 'Semester'),
        ('final', 'Final Grade'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    
    # Компоненты оценки (0-100 баллов)
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    activities = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exam = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    
    # Буквенная оценка (автоматически)
    letter_grade = models.CharField(max_length=2, editable=False, blank=True)
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course', 'period')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'course', 'period']),
            models.Index(fields=['course', 'period']),
        ]
    
    def save(self, *args, **kwargs):
        # Автоматический расчет total и letter_grade
        self.total = self.attendance + self.activities + self.exam
        self.letter_grade = self.calculate_letter_grade()
        super().save(*args, **kwargs)
    
    def calculate_letter_grade(self):
        """Расчет буквенной оценки по шкале университетов КР"""
        if self.total >= 95: return 'A+'
        elif self.total >= 90: return 'A'
        elif self.total >= 85: return 'A-'
        # ... и т.д.
```

**Преимущества:**
- ✅ Единая точка входа для всех оценок
- ✅ Легкая миграция и консистентность
- ✅ Простота в расширении (добавить новый период = 1 строка)
- ✅ Оптимизированные запросы с индексами

---

### 1.2 Проблема: Отсутствие валидации весов компонентов

**Текущая ситуация:**
```python
# В моделях нет проверки, что attendance + activities + exam = 100
attendance = models.DecimalField(max_digits=5, decimal_places=2)
activities = models.DecimalField(max_digits=5, decimal_places=2)
exam = models.DecimalField(max_digits=5, decimal_places=2)
```

**Проблемы:**
- ❌ Преподаватель может поставить attendance=40, activities=40, exam=50 (total=130!)
- ❌ Нет конфигурации весов на уровне курса
- ❌ Все курсы используют одинаковые веса (30/30/40)

**Улучшение:**
```python
class Course(models.Model):
    # ...существующие поля...
    
    # Конфигурация весов (в процентах)
    attendance_weight = models.IntegerField(default=30)
    activities_weight = models.IntegerField(default=30)
    exam_weight = models.IntegerField(default=40)
    
    def clean(self):
        """Валидация весов"""
        total_weight = self.attendance_weight + self.activities_weight + self.exam_weight
        if total_weight != 100:
            raise ValidationError(
                f'Сумма весов должна быть 100%, сейчас {total_weight}%'
            )

class Grade(models.Model):
    # ...
    
    def clean(self):
        """Валидация оценок с учетом весов курса"""
        if self.attendance > self.course.attendance_weight:
            raise ValidationError(
                f'Посещаемость не может быть больше {self.course.attendance_weight}'
            )
        # ... аналогично для activities и exam
```

---

### 1.3 Проблема: Отсутствие истории изменений оценок

**Текущая ситуация:**
- ❌ Нет логирования кто и когда изменил оценку
- ❌ Невозможно откатить изменения
- ❌ Нет аудита для споров со студентами

**Улучшение:**
```python
class GradeHistory(models.Model):
    """История изменений оценок для аудита"""
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    # Старые значения
    old_attendance = models.DecimalField(max_digits=5, decimal_places=2)
    old_activities = models.DecimalField(max_digits=5, decimal_places=2)
    old_exam = models.DecimalField(max_digits=5, decimal_places=2)
    old_total = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Новые значения
    new_attendance = models.DecimalField(max_digits=5, decimal_places=2)
    new_activities = models.DecimalField(max_digits=5, decimal_places=2)
    new_exam = models.DecimalField(max_digits=5, decimal_places=2)
    new_total = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Причина изменения
    reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
```

**Применение:**
```python
# В signals или методе save()
@receiver(pre_save, sender=Grade)
def log_grade_change(sender, instance, **kwargs):
    if instance.pk:  # Если это обновление, а не создание
        old_grade = Grade.objects.get(pk=instance.pk)
        GradeHistory.objects.create(
            grade=instance,
            changed_by=get_current_user(),
            old_attendance=old_grade.attendance,
            # ... и т.д.
        )
```

---

## 2. 🔗 Улучшения логики и связей

### 2.1 Проблема: Слабая связь между Student и Group

**Текущая ситуация:**
```python
class Student(User):
    level = models.CharField(max_length=25, choices=LEVEL)
    department = models.CharField(max_length=200)
```

**Проблемы:**
- ❌ `department` - это просто строка, а не FK
- ❌ Нет формализованной модели Group
- ❌ Невозможно отследить переводы студентов между группами
- ❌ Сложно получить всех студентов группы

**Улучшение:**
```python
class Group(models.Model):
    """Учебная группа (например, CS-22, IS-23)"""
    name = models.CharField(max_length=50, unique=True)  # CS-22
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=LEVEL)
    admission_year = models.IntegerField()  # 2022
    curator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='curated_groups'
    )
    
    # Академический год и семестр
    current_semester = models.ForeignKey(
        Semester, 
        on_delete=models.SET_NULL,
        null=True
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.program})"

class GroupMembership(models.Model):
    """История принадлежности студента к группам"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    # Период членства
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Причина перевода
    REASON_CHOICES = [
        ('admission', 'Поступление'),
        ('transfer', 'Перевод'),
        ('restoration', 'Восстановление'),
        ('graduation', 'Выпуск'),
    ]
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'group', 'start_date')

class Student(User):
    # Удаляем department, level (они теперь в Group)
    
    @property
    def current_group(self):
        """Текущая группа студента"""
        membership = GroupMembership.objects.filter(
            student=self,
            is_active=True
        ).first()
        return membership.group if membership else None
```

**Преимущества:**
- ✅ Формализованная структура групп
- ✅ История переводов студентов
- ✅ Легко получить всех студентов группы
- ✅ Связь с куратором и программой

---

### 2.2 Проблема: CourseAllocation без привязки к семестру

**Текущая ситуация:**
```python
class CourseAllocation(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, related_name='allocated_course')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
```

**Проблемы:**
- ❌ Нет привязки к конкретному семестру
- ❌ Нет информации о группах, которым преподается курс
- ❌ Невозможно отследить нагрузку преподавателя
- ❌ ManyToMany с Course слишком общий

**Улучшение:**
```python
class CourseOffering(models.Model):
    """Предложение курса в конкретном семестре для группы"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'is_lecturer': True}
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Расписание
    schedule = models.JSONField(default=dict)  # {"Monday": ["10:00-11:30"], ...}
    room = models.CharField(max_length=50, blank=True)
    
    # Статус
    STATUS_CHOICES = [
        ('planned', 'Запланирован'),
        ('active', 'Активен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Даты
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Нагрузка (часы)
    lecture_hours = models.IntegerField(default=0)
    practice_hours = models.IntegerField(default=0)
    lab_hours = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('course', 'group', 'semester')
        ordering = ['-semester', 'course']
    
    def __str__(self):
        return f"{self.course} - {self.group} ({self.semester})"
    
    @property
    def total_hours(self):
        return self.lecture_hours + self.practice_hours + self.lab_hours
    
    @property
    def enrollment_count(self):
        """Количество записавшихся студентов"""
        return self.enrollments.filter(status='active').count()

class Enrollment(models.Model):
    """Запись студента на курс"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    offering = models.ForeignKey(
        CourseOffering, 
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Статус записи
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('dropped', 'Отчислен'),
        ('completed', 'Завершён'),
        ('transferred', 'Переведён'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    dropped_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'offering')
```

**Преимущества:**
- ✅ Четкая привязка: Курс → Группа → Семестр → Преподаватель
- ✅ Отслеживание нагрузки преподавателя
- ✅ История записей студентов (active/dropped)
- ✅ Расписание и аудитории

---

### 2.3 Проблема: Отсутствие Prerequisites (пререквизитов)

**Текущая ситуация:**
- ❌ Нет проверки, что студент прошел необходимые курсы
- ❌ Студент может записаться на "Algorithms II" без "Algorithms I"

**Улучшение:**
```python
class Course(models.Model):
    # ...существующие поля...
    
    # Пререквизиты
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='required_for'
    )
    
    # Минимальная оценка для пререквизита
    min_prerequisite_grade = models.CharField(
        max_length=2,
        default='D',
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    
    def can_enroll(self, student):
        """Может ли студент записаться на курс"""
        for prereq in self.prerequisites.all():
            # Проверяем, есть ли оценка по пререквизиту
            try:
                grade = Grade.objects.get(
                    student=student,
                    course=prereq,
                    period='semester'
                )
                if not self._meets_min_grade(grade.letter_grade):
                    return False, f"Требуется оценка {self.min_prerequisite_grade} по курсу {prereq}"
            except Grade.DoesNotExist:
                return False, f"Сначала необходимо завершить курс {prereq}"
        
        return True, "OK"
    
    def _meets_min_grade(self, actual_grade):
        """Проверка минимальной оценки"""
        grade_order = ['F', 'D', 'C', 'B', 'A']
        return grade_order.index(actual_grade[0]) >= grade_order.index(self.min_prerequisite_grade)
```

---

## 3. 🎨 Улучшения UX/UI и производительности

### 3.1 Проблема: N+1 запросы при загрузке оценок

**Текущая ситуация:**
```python
# В представлении
grades = Grade_1st_module.objects.filter(course=course)
for grade in grades:
    print(grade.student.name)  # N+1 запрос!
    print(grade.lecturer.name)  # Ещё один запрос!
```

**Улучшение:**
```python
# Оптимизированный запрос с select_related
grades = Grade.objects.filter(
    course=course,
    period='1st_module'
).select_related(
    'student',
    'student__user',
    'lecturer',
    'course'
).prefetch_related(
    'course__program'
)

# Или создать менеджер
class GradeManager(models.Manager):
    def with_relations(self):
        return self.select_related(
            'student', 'lecturer', 'course'
        ).prefetch_related('course__program')

class Grade(models.Model):
    objects = GradeManager()
    # ...

# Использование
grades = Grade.objects.with_relations().filter(course=course)
```

**Результат:**
- ❌ Было: 1 запрос + N запросов = 1 + 100 = 101 запрос
- ✅ Стало: 1 запрос с JOIN = 1 запрос

---

### 3.2 Проблема: Отсутствие кеширования

**Текущая ситуация:**
- ❌ Каждый раз идет запрос к БД за списком групп
- ❌ Справочники (Programs, Courses) загружаются постоянно

**Улучшение:**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# В модели
from django.core.cache import cache

class Group(models.Model):
    # ...
    
    @classmethod
    def get_active_groups(cls):
        """Кешированный список активных групп"""
        cache_key = 'active_groups'
        groups = cache.get(cache_key)
        
        if groups is None:
            groups = list(cls.objects.filter(is_active=True).select_related('program'))
            cache.set(cache_key, groups, 3600)  # 1 час
        
        return groups
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Инвалидация кеша
        cache.delete('active_groups')

# В views
def get_groups(request):
    groups = Group.get_active_groups()  # Из кеша!
```

---

### 3.3 Проблема: Нет real-time уведомлений

**Текущая ситуация:**
- ❌ Студент не знает, что преподаватель выставил оценки
- ❌ Преподаватель не получает уведомление о новом студенте

**Улучшение:**
```python
# Добавить модель Notification
class Notification(models.Model):
    TYPE_CHOICES = [
        ('grade_posted', 'Оценка выставлена'),
        ('course_enrollment', 'Запись на курс'),
        ('grade_changed', 'Оценка изменена'),
        ('deadline', 'Приближается дедлайн'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# В signals
@receiver(post_save, sender=Grade)
def notify_grade_posted(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.student.user,
            type='grade_posted',
            title='Новая оценка',
            message=f'Преподаватель {instance.lecturer} выставил оценку по курсу {instance.course}',
            link=f'/grades/{instance.id}/'
        )

# WebSocket для real-time (с Django Channels)
# consumers.py
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        await self.channel_layer.group_add(
            f'user_{self.user_id}',
            self.channel_name
        )
        await self.accept()
    
    async def notification_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
```

---

## 4. 🎓 Академические улучшения (специфика КР)

### 4.1 Система академической задолженности

**В университетах КР:**
- Студент может иметь академическую задолженность (долги)
- Разрешено не более 2-3 долгов для перехода на следующий курс
- Есть пересдачи (ресит)

**Улучшение:**
```python
class AcademicDebt(models.Model):
    """Академическая задолженность"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Тип задолженности
    TYPE_CHOICES = [
        ('failed_exam', 'Не сдал экзамен'),
        ('failed_course', 'Не прошел курс'),
        ('attendance', 'Низкая посещаемость'),
        ('not_submitted', 'Не сдал задания'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Статус
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('resolved', 'Закрыта'),
        ('pending_retake', 'Ожидает пересдачи'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Пересдача
    retake_scheduled = models.DateTimeField(null=True, blank=True)
    retake_attempts = models.IntegerField(default=0)
    max_retake_attempts = models.IntegerField(default=3)
    
    class Meta:
        unique_together = ('student', 'course', 'semester')

class Student(User):
    # ...
    
    def can_progress_to_next_year(self):
        """Может ли студент перейти на следующий курс"""
        active_debts = AcademicDebt.objects.filter(
            student=self,
            status='active'
        ).count()
        
        # Правило: не более 2 долгов
        return active_debts <= 2
    
    @property
    def academic_status(self):
        """Академический статус"""
        debt_count = AcademicDebt.objects.filter(
            student=self,
            status='active'
        ).count()
        
        if debt_count == 0:
            return 'excellent'
        elif debt_count <= 2:
            return 'warning'
        else:
            return 'critical'
```

---

### 4.2 ГОСТы и стандарты КР

**В университетах КР:**
- Обязательны государственные стандарты (ГОСы)
- Определенное количество кредитов по категориям
- Обязательные дисциплины (государственный компонент)

**Улучшение:**
```python
class Course(models.Model):
    # ...существующие поля...
    
    # Классификация по ГОСу
    CATEGORY_CHOICES = [
        ('general', 'Общеобразовательный'),
        ('core', 'Базовый (государственный компонент)'),
        ('major', 'Профилирующий'),
        ('elective', 'Элективный'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Кредиты (ECTS)
    credits = models.IntegerField()
    
    # Обязательность
    is_mandatory = models.BooleanField(default=False)
    
    # Язык преподавания
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('ky', 'Кыргызский'),
        ('en', 'Английский'),
    ]
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ru')

class Program(models.Model):
    # ...
    
    # Требования ГОСа
    min_total_credits = models.IntegerField(default=240)  # Для бакалавра
    min_core_credits = models.IntegerField(default=60)
    min_major_credits = models.IntegerField(default=120)
    min_elective_credits = models.IntegerField(default=60)
    
    def validate_curriculum(self):
        """Проверка соответствия ГОСу"""
        courses = Course.objects.filter(program=self)
        
        total_credits = courses.aggregate(Sum('credits'))['credits__sum'] or 0
        core_credits = courses.filter(category='core').aggregate(Sum('credits'))['credits__sum'] or 0
        major_credits = courses.filter(category='major').aggregate(Sum('credits'))['credits__sum'] or 0
        elective_credits = courses.filter(category='elective').aggregate(Sum('credits'))['credits__sum'] or 0
        
        errors = []
        if total_credits < self.min_total_credits:
            errors.append(f'Недостаточно кредитов: {total_credits}/{self.min_total_credits}')
        if core_credits < self.min_core_credits:
            errors.append(f'Недостаточно базовых кредитов: {core_credits}/{self.min_core_credits}')
        
        return len(errors) == 0, errors
```

---

### 4.3 Стипендии и академическая успеваемость

**В университетах КР:**
- Стипендия зависит от среднего балла (GPA)
- Социальные стипендии
- Гранты

**Улучшение:**
```python
class Scholarship(models.Model):
    """Стипендия"""
    TYPE_CHOICES = [
        ('academic', 'Академическая'),
        ('social', 'Социальная'),
        ('grant', 'Грант'),
        ('presidential', 'Президентская'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Критерии
    min_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    max_debts = models.IntegerField(default=0)
    requires_social_status = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)

class ScholarshipRecipient(models.Model):
    """Получатель стипендии"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Статус
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('suspended', 'Приостановлена'),
        ('revoked', 'Отменена'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Даты
    granted_at = models.DateField()
    expires_at = models.DateField(null=True, blank=True)
    
    # GPA на момент назначения
    gpa_at_grant = models.DecimalField(max_digits=3, decimal_places=2)

class Student(User):
    # ...
    
    def calculate_gpa(self, semester=None):
        """Расчет GPA (Grade Point Average)"""
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.67,
            'B+': 3.33, 'B': 3.0, 'B-': 2.67,
            'C+': 2.33, 'C': 2.0, 'C-': 1.67,
            'D+': 1.33, 'D': 1.0, 'F': 0.0
        }
        
        grades_query = Grade.objects.filter(student=self, period='semester')
        if semester:
            grades_query = grades_query.filter(course__semester=semester)
        
        grades = grades_query.select_related('course')
        
        total_points = 0
        total_credits = 0
        
        for grade in grades:
            points = grade_points.get(grade.letter_grade, 0)
            credits = grade.course.credits
            total_points += points * credits
            total_credits += credits
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    
    def is_eligible_for_scholarship(self, scholarship):
        """Проверка права на стипендию"""
        gpa = self.calculate_gpa()
        debt_count = AcademicDebt.objects.filter(student=self, status='active').count()
        
        if gpa < scholarship.min_gpa:
            return False, f'Недостаточный GPA: {gpa} < {scholarship.min_gpa}'
        
        if debt_count > scholarship.max_debts:
            return False, f'Слишком много долгов: {debt_count} > {scholarship.max_debts}'
        
        return True, 'Соответствует критериям'
```

---

## 5. 🔒 Системные улучшения безопасности

### 5.1 Проблема: Слабая система прав доступа

**Текущая ситуация:**
```python
# Только декораторы @lecturer_required, @student_required
# Нет гранулярного контроля доступа
```

**Улучшение:**
```python
# Использование django-guardian для object-level permissions
from guardian.shortcuts import assign_perm, get_objects_for_user

class CourseOffering(models.Model):
    # ...
    
    class Meta:
        permissions = [
            ('view_grades', 'Can view grades'),
            ('edit_grades', 'Can edit grades'),
            ('approve_grades', 'Can approve grades'),
        ]

# При создании CourseOffering
def create_course_offering(lecturer, course, group):
    offering = CourseOffering.objects.create(
        lecturer=lecturer,
        course=course,
        group=group
    )
    
    # Назначаем права преподавателю
    assign_perm('view_grades', lecturer, offering)
    assign_perm('edit_grades', lecturer, offering)
    
    # Права студентам
    for student in group.students.all():
        assign_perm('view_grades', student.user, offering)
    
    return offering

# В представлении
def edit_grades(request, offering_id):
    offering = get_object_or_404(CourseOffering, id=offering_id)
    
    # Проверка прав
    if not request.user.has_perm('edit_grades', offering):
        return HttpResponseForbidden()
    
    # ...
```

---

### 5.2 Проблема: Нет защиты от мошенничества с оценками

**Улучшение:**
```python
class GradeApproval(models.Model):
    """Система одобрения оценок"""
    grade = models.OneToOneField(Grade, on_delete=models.CASCADE)
    
    # Кто выставил
    submitted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_grades'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Кто проверил (зав. кафедрой)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_grades'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Статус
    STATUS_CHOICES = [
        ('pending', 'Ожидает проверки'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Комментарий при отклонении
    rejection_reason = models.TextField(blank=True)
    
    # Цифровая подпись (для защиты)
    digital_signature = models.CharField(max_length=256, blank=True)
    
    def generate_signature(self):
        """Генерация цифровой подписи"""
        import hashlib
        data = f"{self.grade.id}{self.submitted_by.id}{self.submitted_at}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        if not self.digital_signature:
            self.digital_signature = self.generate_signature()
        super().save(*args, **kwargs)

# Настройка workflow
class GradeWorkflow:
    @staticmethod
    def submit_for_approval(grades, lecturer):
        """Отправка оценок на одобрение"""
        for grade in grades:
            GradeApproval.objects.create(
                grade=grade,
                submitted_by=lecturer,
                status='pending'
            )
    
    @staticmethod
    def approve_grades(grades, approver):
        """Одобрение оценок заведующим"""
        for grade in grades:
            approval = GradeApproval.objects.get(grade=grade)
            approval.approved_by = approver
            approval.approved_at = timezone.now()
            approval.status = 'approved'
            approval.save()
```

---

## 6. 📊 Аналитика и отчётность

### 6.1 Дашборд аналитики для администрации

**Улучшение:**
```python
# analytics/models.py
class AnalyticsReport(models.Model):
    """Аналитические отчёты"""
    REPORT_TYPE_CHOICES = [
        ('enrollment', 'Статистика записей'),
        ('performance', 'Успеваемость'),
        ('attendance', 'Посещаемость'),
        ('retention', 'Удержание студентов'),
        ('lecturer_load', 'Нагрузка преподавателей'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Данные
    data = models.JSONField()
    
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-generated_at']

# analytics/services.py
class AnalyticsService:
    @staticmethod
    def generate_performance_report(semester):
        """Отчёт по успеваемости"""
        grades = Grade.objects.filter(
            course__semester=semester,
            period='semester'
        )
        
        # Распределение оценок
        grade_distribution = grades.values('letter_grade').annotate(
            count=Count('id')
        )
        
        # Средний балл по программам
        avg_by_program = grades.values(
            'student__current_group__program__name'
        ).annotate(
            avg_total=Avg('total')
        )
        
        # Количество долгов
        debts = AcademicDebt.objects.filter(
            semester=semester,
            status='active'
        ).count()
        
        return {
            'grade_distribution': list(grade_distribution),
            'avg_by_program': list(avg_by_program),
            'total_debts': debts,
            'total_students': grades.values('student').distinct().count(),
        }
    
    @staticmethod
    def generate_lecturer_load_report(semester):
        """Отчёт по нагрузке преподавателей"""
        offerings = CourseOffering.objects.filter(
            semester=semester
        ).select_related('lecturer', 'course', 'group')
        
        lecturer_stats = {}
        for offering in offerings:
            lecturer_id = offering.lecturer.id
            if lecturer_id not in lecturer_stats:
                lecturer_stats[lecturer_id] = {
                    'name': offering.lecturer.get_full_name(),
                    'courses': [],
                    'total_hours': 0,
                    'total_students': 0,
                }
            
            lecturer_stats[lecturer_id]['courses'].append({
                'course': offering.course.title,
                'group': offering.group.name,
                'hours': offering.total_hours,
                'students': offering.enrollment_count,
            })
            lecturer_stats[lecturer_id]['total_hours'] += offering.total_hours
            lecturer_stats[lecturer_id]['total_students'] += offering.enrollment_count
        
        return lecturer_stats
```

---

### 6.2 Экспорт данных в различные форматы

**Улучшение:**
```python
# export/services.py
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

class ExportService:
    @staticmethod
    def export_grades_to_excel(course_offering):
        """Экспорт оценок в Excel"""
        grades = Grade.objects.filter(
            course=course_offering.course,
            period='semester'
        ).select_related('student')
        
        # Создаем DataFrame
        data = []
        for grade in grades:
            data.append({
                'ID': grade.student.id,
                'ФИО': grade.student.get_full_name(),
                'Группа': grade.student.current_group.name,
                'Посещаемость': float(grade.attendance),
                'Активность': float(grade.activities),
                'Экзамен': float(grade.exam),
                'Итого': float(grade.total),
                'Оценка': grade.letter_grade,
            })
        
        df = pd.DataFrame(data)
        
        # Создаем Excel файл с форматированием
        wb = Workbook()
        ws = wb.active
        ws.title = "Оценки"
        
        # Заголовок
        ws.append(['Ведомость оценок'])
        ws.merge_cells('A1:H1')
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        
        # Информация о курсе
        ws.append([f'Курс: {course_offering.course.title}'])
        ws.append([f'Преподаватель: {course_offering.lecturer.get_full_name()}'])
        ws.append([f'Группа: {course_offering.group.name}'])
        ws.append([])  # Пустая строка
        
        # Заголовки столбцов
        headers = list(df.columns)
        ws.append(headers)
        
        # Форматирование заголовков
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        for cell in ws[6]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Данные
        for _, row in df.iterrows():
            ws.append(row.tolist())
        
        # Автоширина столбцов
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max_length + 2
        
        return wb
    
    @staticmethod
    def export_transcript(student):
        """Экспорт транскрипта студента"""
        grades = Grade.objects.filter(
            student=student,
            period='semester'
        ).select_related('course', 'course__program').order_by('course__semester')
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Транскрипт"
        
        # Шапка
        ws.append(['АКАДЕМИЧЕСКАЯ СПРАВКА (ТРАНСКРИПТ)'])
        ws.merge_cells('A1:G1')
        ws['A1'].font = Font(size=18, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        
        ws.append([])
        ws.append([f'Студент: {student.get_full_name()}'])
        ws.append([f'ID: {student.id}'])
        ws.append([f'Программа: {student.current_group.program.title}'])
        ws.append([f'Группа: {student.current_group.name}'])
        ws.append([f'GPA: {student.calculate_gpa()}'])
        ws.append([])
        
        # Заголовки
        ws.append(['Семестр', 'Код курса', 'Название курса', 'Кредиты', 'Оценка', 'Баллы', 'Преподаватель'])
        
        # Данные по семестрам
        current_semester = None
        for grade in grades:
            semester = grade.course.semester
            if current_semester != semester:
                ws.append([])
                ws.append([f'{semester}', '', '', '', '', '', ''])
                current_semester = semester
            
            ws.append([
                '',
                grade.course.code,
                grade.course.title,
                grade.course.credits,
                grade.letter_grade,
                float(grade.total),
                grade.lecturer.get_full_name() if grade.lecturer else '-'
            ])
        
        return wb
```

---

## 7. 🔌 Интеграции и автоматизация

### 7.1 Интеграция с платёжными системами

**Для университетов КР:**
- Оплата обучения онлайн (Элсом, О!, MBank)
- Контроль оплаты перед записью на курс

**Улучшение:**
```python
# payments/models.py
class Payment(models.Model):
    """Платежи студентов"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    # Сумма
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KGS')
    
    # Тип платежа
    TYPE_CHOICES = [
        ('tuition', 'Оплата обучения'),
        ('dormitory', 'Общежитие'),
        ('library', 'Библиотека'),
        ('services', 'Услуги'),
    ]
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Статус
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'В обработке'),
        ('completed', 'Оплачено'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Платёжная система
    PROVIDER_CHOICES = [
        ('elsom', 'Элсом'),
        ('o', 'О!'),
        ('mbank', 'MBank'),
        ('balance', 'Balance'),
    ]
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, blank=True)
    
    # Данные транзакции
    transaction_id = models.CharField(max_length=200, unique=True, blank=True)
    provider_response = models.JSONField(default=dict)
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

class Student(User):
    # ...
    
    def has_paid_tuition(self, semester):
        """Проверка оплаты за семестр"""
        payment = Payment.objects.filter(
            student=self,
            semester=semester,
            payment_type='tuition',
            status='completed'
        ).first()
        
        return payment is not None
    
    def can_enroll(self, course_offering):
        """Может ли записаться на курс"""
        # Проверка оплаты
        if not self.has_paid_tuition(course_offering.semester):
            return False, 'Необходимо оплатить обучение'
        
        # Проверка пререквизитов
        can_enroll, reason = course_offering.course.can_enroll(self)
        if not can_enroll:
            return False, reason
        
        return True, 'OK'

# payments/services.py
class PaymentService:
    @staticmethod
    def create_payment_link(student, semester, amount):
        """Создание ссылки на оплату"""
        payment = Payment.objects.create(
            student=student,
            semester=semester,
            amount=amount,
            payment_type='tuition',
            status='pending'
        )
        
        # Генерация ссылки для Элсом (пример)
        # В реальности - интеграция с API платёжной системы
        payment_url = f"https://elsom.kg/pay?order_id={payment.id}&amount={amount}"
        
        return payment, payment_url
    
    @staticmethod
    def handle_payment_callback(transaction_id, status, provider_data):
        """Обработка callback от платёжной системы"""
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.status = 'completed' if status == 'success' else 'failed'
            payment.provider_response = provider_data
            payment.paid_at = timezone.now()
            payment.save()
            
            # Отправка уведомления студенту
            if payment.status == 'completed':
                Notification.objects.create(
                    recipient=payment.student.user,
                    type='payment_success',
                    title='Оплата принята',
                    message=f'Ваш платеж на сумму {payment.amount} KGS принят',
                )
            
            return True
        except Payment.DoesNotExist:
            return False
```

---

### 7.2 Автоматизация рассылок

**Улучшение:**
```python
# notifications/tasks.py (с Celery)
from celery import shared_task

@shared_task
def send_grade_notifications(course_offering_id):
    """Автоматическая рассылка уведомлений об оценках"""
    offering = CourseOffering.objects.get(id=course_offering_id)
    grades = Grade.objects.filter(
        course=offering.course,
        period='semester'
    ).select_related('student')
    
    for grade in grades:
        # Email
        send_mail(
            subject=f'Оценка по курсу {offering.course.title}',
            message=f'Здравствуйте, {grade.student.first_name}!\n\n'
                    f'Ваша оценка: {grade.letter_grade} ({grade.total} баллов)\n'
                    f'Преподаватель: {offering.lecturer.get_full_name()}',
            from_email='noreply@salymbekov.kg',
            recipient_list=[grade.student.email],
        )
        
        # SMS (через SMS.kg API)
        send_sms(
            phone=grade.student.phone,
            message=f'Оценка по {offering.course.code}: {grade.letter_grade}'
        )
        
        # Push-уведомление
        send_push_notification(
            user=grade.student.user,
            title='Новая оценка',
            body=f'{offering.course.title}: {grade.letter_grade}'
        )

@shared_task
def send_deadline_reminders():
    """Напоминания о приближающихся дедлайнах"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Экзамены завтра
    offerings = CourseOffering.objects.filter(
        end_date=tomorrow
    ).select_related('course', 'group')
    
    for offering in offerings:
        enrollments = Enrollment.objects.filter(
            offering=offering,
            status='active'
        ).select_related('student')
        
        for enrollment in enrollments:
            Notification.objects.create(
                recipient=enrollment.student.user,
                type='deadline',
                title='Завтра экзамен!',
                message=f'Напоминаем: завтра экзамен по курсу {offering.course.title}'
            )

@shared_task
def generate_weekly_reports():
    """Еженедельная генерация отчётов"""
    current_semester = Semester.objects.filter(is_current=True).first()
    
    # Отчёт по успеваемости
    performance_data = AnalyticsService.generate_performance_report(current_semester)
    AnalyticsReport.objects.create(
        report_type='performance',
        semester=current_semester,
        data=performance_data
    )
    
    # Отчёт по нагрузке преподавателей
    load_data = AnalyticsService.generate_lecturer_load_report(current_semester)
    AnalyticsReport.objects.create(
        report_type='lecturer_load',
        semester=current_semester,
        data=load_data
    )

# Настройка периодических задач (celery beat)
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-deadline-reminders-daily': {
        'task': 'notifications.tasks.send_deadline_reminders',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
    'generate-weekly-reports': {
        'task': 'notifications.tasks.generate_weekly_reports',
        'schedule': crontab(day_of_week='monday', hour=6, minute=0),  # Каждый понедельник в 6:00
    },
}
```

---

### 7.3 Интеграция с электронной библиотекой

**Улучшение:**
```python
# library/models.py
class LibraryResource(models.Model):
    """Ресурсы библиотеки"""
    TYPE_CHOICES = [
        ('book', 'Книга'),
        ('article', 'Статья'),
        ('thesis', 'Диссертация'),
        ('journal', 'Журнал'),
    ]
    
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Файл (PDF)
    file = models.FileField(upload_to='library/', blank=True)
    
    # Связь с курсами
    courses = models.ManyToManyField(Course, related_name='library_resources')
    
    # Доступность
    is_available_online = models.BooleanField(default=True)
    physical_copies = models.IntegerField(default=0)
    
    # Метаданные
    publisher = models.CharField(max_length=200, blank=True)
    year = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=2, default='ru')
    
    created_at = models.DateTimeField(auto_now_add=True)

class LibraryLoan(models.Model):
    """Выдача книг"""
    resource = models.ForeignKey(LibraryResource, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    # Даты
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    
    # Статус
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('returned', 'Возвращена'),
        ('overdue', 'Просрочена'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Штраф за просрочку
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def is_overdue(self):
        if self.status == 'active' and self.due_date < timezone.now().date():
            return True
        return False
    
    def calculate_fine(self):
        """Расчет штрафа (10 сом за день)"""
        if self.is_overdue:
            days_overdue = (timezone.now().date() - self.due_date).days
            self.fine_amount = days_overdue * 10
            self.status = 'overdue'
            self.save()

# Автоматическая задача для проверки просрочек
@shared_task
def check_library_overdue():
    """Проверка просроченных книг"""
    loans = LibraryLoan.objects.filter(status='active', due_date__lt=timezone.now().date())
    
    for loan in loans:
        loan.calculate_fine()
        
        # Уведомление студента
        Notification.objects.create(
            recipient=loan.student.user,
            type='library_overdue',
            title='Просрочка возврата книги',
            message=f'Книга "{loan.resource.title}" просрочена. Штраф: {loan.fine_amount} KGS'
        )
```

---

## 📊 Приоритизация улучшений

### 🔴 Критические (внедрить немедленно)

1. **Унификация моделей оценок** - устранить дублирование Grade_1st_module, Grade_2nd_module, Grade_semester
2. **История изменений оценок (GradeHistory)** - для аудита и разрешения споров
3. **Оптимизация запросов** - select_related/prefetch_related для устранения N+1

### 🟠 Высокий приоритет (1-2 месяца)

4. **Формализация групп (Group + GroupMembership)** - для корректной работы с группами
5. **Система CourseOffering + Enrollment** - замена CourseAllocation
6. **Валидация весов компонентов оценок** - предотвращение ошибок при выставлении оценок
7. **Академические задолжен