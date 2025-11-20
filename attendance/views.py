from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import ScheduleItem, Attendance, LessonTime
from .serializers import (
    LessonTimeSerializer,
    ScheduleItemSerializer,
    StudentScheduleItemSerializer,
    LecturerScheduleItemSerializer,
    AdminScheduleItemSerializer,
    AttendanceSerializer,
    StudentAttendanceSerializer,
    LecturerAttendanceSerializer,
    AdminAttendanceSerializer,
    BulkAttendancesUpdateSerializer
)
from core.permissions import IsAdminOrLecturer, IsLecturer


class LessonTimeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления временами уроков.
    Только администраторы могут создавать и изменять времена уроков.
    """
    serializer_class = LessonTimeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']
    
    def get_queryset(self):
        """
        Фильтруем времена уроков по админу
        """
        user = self.request.user
        if user.is_superuser:
            return LessonTime.objects.filter(admin=user)
        elif hasattr(user, 'admin') and user.admin:
            # Преподаватели и студенты могут видеть времена уроков своего админа
            return LessonTime.objects.filter(admin=user.admin)
        return LessonTime.objects.none()
    
    def get_serializer_context(self):
        """Передаем admin в контекст сериализатора"""
        context = super().get_serializer_context()
        context['admin'] = self.request.user if self.request.user.is_superuser else getattr(self.request.user, 'admin', None)
        return context


class ScheduleItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления расписанием.
    
    - Студенты: только чтение своего расписания
    - Преподаватели: чтение и редактирование расписания своих групп
    - Администраторы: полный доступ
    """
    queryset = ScheduleItem.objects.select_related('course', 'group').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'group', 'day']
    search_fields = ['course__title', 'course__code', 'group__name']
    ordering_fields = ['day', 'start', 'order']
    ordering = ['day', 'start', 'order']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Студенты видят только расписание своей группы
        if hasattr(user, 'student'):
            student = user.student
            if student.group:
                queryset = queryset.filter(group=student.group)
            else:
                queryset = queryset.none()
        
        # Преподаватели видят расписание групп, где они преподают
        elif user.is_lecturer:
            # Получаем курсы и группы преподавателя через CourseAllocation
            from course.models import CourseAllocation
            allocations = CourseAllocation.objects.filter(lecturer=user)
            
            # Фильтруем расписание по курсам и группам преподавателя
            from django.db.models import Q
            queries = Q()
            for allocation in allocations:
                course_ids = allocation.courses.values_list('id', flat=True)
                if allocation.group:
                    # Если указана группа, фильтруем по курсу И группе
                    queries |= Q(course__in=course_ids, group=allocation.group)
                else:
                    # Если группа не указана, показываем все группы для этих курсов
                    queries |= Q(course__in=course_ids)
            
            queryset = queryset.filter(queries) if queries else queryset.none()
        
        return queryset

    def get_serializer_class(self):
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            return AdminScheduleItemSerializer
        elif user.is_lecturer:
            return LecturerScheduleItemSerializer
        elif hasattr(user, 'student'):
            return StudentScheduleItemSerializer
        
        return ScheduleItemSerializer

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от действия
        Только администраторы могут управлять расписанием
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Создание, редактирование и удаление только для админов
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='group_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID группы'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='group/(?P<group_id>[^/.]+)')
    def by_group(self, request, group_id=None):
        """Получить расписание по конкретной группе"""
        queryset = self.get_queryset().filter(group_id=group_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='day',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='День недели'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='day/(?P<day>[^/.]+)')
    def by_day(self, request, day=None):
        """Получить расписание на конкретный день"""
        queryset = self.get_queryset().filter(day=day)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_schedule(self, request):
        """Получить расписание текущего пользователя"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления посещаемостью.
    
    - Студенты: только чтение своей посещаемости
    - Преподаватели: чтение и отметка посещаемости студентов на своих занятиях
    - Администраторы: полный доступ
    """
    queryset = Attendance.objects.select_related(
        'Student', 'Student__student', 'shcedule', 'shcedule__course', 'shcedule__group'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['Student', 'status', 'shcedule', 'shcedule__course', 'shcedule__day']
    search_fields = ['Student__student__first_name', 'Student__student__last_name', 'shcedule__course__title']
    ordering_fields = ['shcedule__day', 'shcedule__start']
    ordering = ['shcedule__day', 'shcedule__start']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Студенты видят только свою посещаемость
        if hasattr(user, 'student'):
            queryset = queryset.filter(Student=user.student)
        
        # Преподаватели видят посещаемость на своих занятиях
        elif user.is_lecturer:
            from course.models import CourseAllocation
            allocations = CourseAllocation.objects.filter(lecturer=user)
            
            # Фильтруем посещаемость по курсам и группам преподавателя
            from django.db.models import Q
            queries = Q()
            for allocation in allocations:
                course_ids = allocation.courses.values_list('id', flat=True)
                if allocation.group:
                    queries |= Q(shcedule__course__in=course_ids, shcedule__group=allocation.group)
                else:
                    queries |= Q(shcedule__course__in=course_ids)
            
            queryset = queryset.filter(queries) if queries else queryset.none()
        
        return queryset

    def get_serializer_class(self):
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            return AdminAttendanceSerializer
        elif user.is_lecturer:
            return LecturerAttendanceSerializer
        elif hasattr(user, 'student'):
            return StudentAttendanceSerializer
        
        return AttendanceSerializer

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от действия
        """
        if self.action in ['create', 'destroy']:
            # Создание и удаление только для админов
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['update', 'partial_update', 'mark_attendance', 'bulk_update']:
            # Обновление для админов и преподавателей
            permission_classes = [IsAuthenticated, IsAdminOrLecturer]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='schedule_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID занятия по расписанию'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='schedule/(?P<schedule_id>[^/.]+)')
    def by_schedule(self, request, schedule_id=None):
        """Получить посещаемость по конкретному занятию"""
        queryset = self.get_queryset().filter(shcedule_id=schedule_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='student_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID студента'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def by_student(self, request, student_id=None):
        """Получить посещаемость конкретного студента"""
        queryset = self.get_queryset().filter(Student_id=student_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_attendance(self, request):
        """Получить посещаемость текущего студента"""
        if hasattr(request.user, 'student'):
            queryset = self.get_queryset().filter(Student=request.user.student)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Только студенты могут получить свою посещаемость'},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику посещаемости"""
        queryset = self.get_queryset()
        
        total = queryset.count()
        present = queryset.filter(status=True).count()
        absent = queryset.filter(status=False).count()
        
        attendance_rate = (present / total * 100) if total > 0 else 0
        
        return Response({
            'total': total,
            'present': present,
            'absent': absent,
            'attendance_rate': round(attendance_rate, 2)
        })

    @extend_schema(
        request=BulkAttendancesUpdateSerializer,
        responses={200: AttendanceSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrLecturer])
    def bulk_update(self, request):
        """
        Массовое обновление посещаемости для занятия.
        Ожидается формат:
        {
            "schedule_id": 1,
            "attendances": [
                {"student_id": 1, "status": true},
                {"student_id": 2, "status": false}
            ]
        }
        """
        serializer = BulkAttendancesUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        schedule_id = serializer.validated_data['schedule_id']
        attendances_data = serializer.validated_data['attendances']
        
        # Проверяем, что расписание существует
        try:
            schedule = ScheduleItem.objects.get(id=schedule_id)
        except ScheduleItem.DoesNotExist:
            return Response(
                {'error': 'Занятие не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем права преподавателя
        if request.user.is_lecturer and not request.user.is_staff:
            from course.models import CourseAllocation
            # Проверяем, что преподаватель назначен на этот курс И группу
            has_permission = CourseAllocation.objects.filter(
                lecturer=request.user,
                courses=schedule.course,
                group=schedule.group
            ).exists()
            
            if not has_permission:
                return Response(
                    {'error': 'У вас нет прав для отметки посещаемости на этом занятии'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        updated_attendances = []
        
        with transaction.atomic():
            for attendance_data in attendances_data:
                student_id = attendance_data['student_id']
                status_value = attendance_data['status']
                
                # Обновляем или создаем запись о посещаемости
                attendance, created = Attendance.objects.update_or_create(
                    Student_id=student_id,
                    shcedule_id=schedule_id,
                    defaults={'status': status_value}
                )
                updated_attendances.append(attendance)
        
        serializer = self.get_serializer(updated_attendances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
