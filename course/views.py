from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django_filters.views import FilterView

from accounts.decorators import lecturer_required, student_required
from accounts.models import Student
from core.models import Semester

from course.models import (
    Course,
    CourseAllocation,
)


from django.utils.translation import gettext_lazy as _
from .models import Course


# ########################################################
# Program Views
# ########################################################

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from core.models import Program
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model


from .serializers import CourseAllocationSerializer,  CourseSerializer, StudentCoursesSerializer
from rest_framework import generics


User = get_user_model()




class CourseListCreateAPIView(APIView):
    """
    API View для создания нового курса и получения списка курсов
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Разрешить создание курсов только администраторам
        """
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

    def get(self, request):
        """
        Получить список курсов с фильтрацией по admin
        """
        user = request.user
        # Фильтруем курсы по админу
        if user.is_superuser:
            courses = Course.objects.filter(admin=user)
        elif hasattr(user, 'admin') and user.admin:
            courses = Course.objects.filter(admin=user.admin)
        else:
            courses = Course.objects.none()
        
        query = request.GET.get('q', None)
        program = request.GET.get('program', None)
        level = request.GET.get('level', None)
        year = request.GET.get('year', None)
        semester = request.GET.get('semester', None)
        is_elective = request.GET.get('is_elective', None)

        # Поиск
        if query:
            courses = courses.filter(
                Q(title__icontains=query) | 
                Q(code__icontains=query) | 
                Q(summary__icontains=query)
            )

        # Фильтрация
        if program:
            courses = courses.filter(program_id=program)
        if level:
            courses = courses.filter(level=level)
        if year:
            courses = courses.filter(year=year)
        if semester:
            courses = courses.filter(semester=semester)
        if is_elective is not None:
            is_elective_bool = is_elective.lower() in ['true', '1', 'yes']
            courses = courses.filter(is_elective=is_elective_bool)

        serializer = CourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        request=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def post(self, request):
        """
        Создать новый курс
        """
        serializer = CourseSerializer(data=request.data, context={'request': request, 'admin': request.user})
        
        if serializer.is_valid():
            course = serializer.save()
            return Response(
                CourseSerializer(course, context={'request': request}).data,
                status=status.HTTP_201_CREATED 
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailAPIView(APIView):
    """
    API View для получения, обновления и удаления конкретного курса
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Разрешить изменение и удаление только администраторам
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

    def get_object(self, pk, user):
        """
        Получить курс по id с учетом admin или вернуть None
        """
        try:
            if user.is_superuser:
                return Course.objects.get(pk=pk, admin=user)
            elif hasattr(user, 'admin') and user.admin:
                return Course.objects.get(pk=pk, admin=user.admin)
            return None
        except Course.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Получить детальную информацию о курсе
        """
        course = self.get_object(pk, request.user)
        if not course:
            return Response(
                {'detail': _('Course not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CourseSerializer(course, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        request=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def put(self, request, pk):
        """
        Полное обновление курса
        """
        course = self.get_object(pk, request.user)
        if not course:
            return Response(
                {'detail': _('Course not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CourseSerializer(course, data=request.data, context={'request': request})
        if serializer.is_valid():
            updated_course = serializer.save()
            return Response(CourseSerializer(updated_course, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CourseSerializer,
        responses={201: CourseSerializer}
    )  
    def patch(self, request, pk):
        """Частичное обновление курса """
        course = self.get_object(pk, request.user)
        if not course:
            return Response(
                {'detail': _('Course not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CourseSerializer(course, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_course = serializer.save()
            return Response(CourseSerializer(updated_course, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def delete(self, request, pk):
        """
        Удалить курс
        """
        course = self.get_object(pk, request.user)
        if not course:
            return Response(
                {'detail': _('Course not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

        course_title = str(course)
        course.delete()
        return Response(
            {'detail': _(f'Course "{course_title}" has been deleted successfully.')},
            status=status.HTTP_204_NO_CONTENT
        )



class CourseAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = CourseAllocationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['lecturer', 'semester']
    search_fields = ['lecturer__first_name', 'lecturer__last_name', 'lecturer__email', 'courses__title', 'courses__code']
    ordering_fields = ['lecturer__first_name', 'lecturer__last_name']
    ordering = ['lecturer__first_name']

    def get_queryset(self):
        user = self.request.user
        
        # Фильтруем по admin
        if user.is_superuser:
            queryset = CourseAllocation.objects.filter(admin=user)
        elif user.is_lecturer:
            # Для преподавателей - только свои назначения
            queryset = CourseAllocation.objects.filter(lecturer=user)
        elif hasattr(user, 'admin') and user.admin:
            queryset = CourseAllocation.objects.filter(admin=user.admin)
        else:
            queryset = CourseAllocation.objects.none()
        
        # Предзагрузка связанных данных для оптимизации
        queryset = queryset.select_related('lecturer').prefetch_related('courses')
        
        return queryset
    
    def get_serializer_context(self):
        """Передаем admin в контекст сериализатора"""
        context = super().get_serializer_context()
        context['admin'] = self.request.user if self.request.user.is_superuser else getattr(self.request.user, 'admin', None)
        return context

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def my_allocations(self, request):
        """Получить назначения текущего пользователя (для преподавателей)"""
        if not request.user.is_lecturer:
            return Response(
                {"detail": "Only lecturers can view their allocations"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        allocations = self.get_queryset().filter(lecturer=request.user)
        serializer = self.get_serializer(allocations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_courses(self, request, pk=None):
        """Добавить курсы к существующему назначению"""
        allocation = self.get_object()
        course_ids = request.data.get('course_ids', [])
        
        if not course_ids:
            return Response(
                {"detail": "course_ids field is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            courses = Course.objects.filter(id__in=course_ids)
            allocation.courses.add(*courses)
            return Response({"detail": "Courses added successfully"})
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def remove_courses(self, request, pk=None):
        """Удалить курсы из назначения"""
        allocation = self.get_object()
        course_ids = request.data.get('course_ids', [])
        
        if not course_ids:
            return Response(
                {"detail": "course_ids field is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            courses = Course.objects.filter(id__in=course_ids)
            allocation.courses.remove(*courses)
            return Response({"detail": "Courses removed successfully"})
        except Exception as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

class StudentCoursesListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentCoursesSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'student'):
            return CourseAllocation.objects.filter(group=self.request.user.student.group)
        return CourseAllocation.objects.none()