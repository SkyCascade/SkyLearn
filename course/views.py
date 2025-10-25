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
from course.filters import CourseAllocationFilter, ProgramFilter
from course.models import (
    Course,
    CourseAllocation,
    Program,
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
from .models import Program
from .serializers import ProgramSerializer
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


class ProgramListAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        query = request.GET.get('q', None)
        if query:
            programs = Program.objects.search(query)
        else:
            programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=ProgramSerializer,
        responses={201: ProgramSerializer}
    )
    def post(self, request):
        serializer = ProgramSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgramDetailAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def get_object(self, pk):
        try:
            return Program.objects.get(pk=pk)
        except Program.DoesNotExist:
            return None
    
    def get(self, request, pk):
        program = self.get_object(pk)
        if not program:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProgramSerializer(program)
        return Response(serializer.data)
    
    @extend_schema(
        request=ProgramSerializer,
        responses={201: ProgramSerializer}
    )
    def put(self, request, pk):
        program = self.get_object(pk)
        if not program:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProgramSerializer(program, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        request=ProgramSerializer,
        responses={201: ProgramSerializer}
    )
    def patch(self, request, pk):
        program = self.get_object(pk)
        if not program:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProgramSerializer(program, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        request=ProgramSerializer,
        responses={201: ProgramSerializer}
    )
    def delete(self, request, pk):
        program = self.get_object(pk)
        if not program:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        program.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





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
        Получить список всех курсов с поддержкой поиска
        """
        query = request.GET.get('q', None)
        program = request.GET.get('program', None)
        level = request.GET.get('level', None)
        year = request.GET.get('year', None)
        semester = request.GET.get('semester', None)
        is_elective = request.GET.get('is_elective', None)

        courses = Course.objects.all()

        # Поиск
        if query:
            courses = courses.search(query)

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
        serializer = CourseSerializer(data=request.data, context={'request': request})
        
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

    def get_object(self, pk):
        """
        Получить курс по id или вернуть 404
        """
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Получить детальную информацию о курсе
        """
        course = self.get_object(pk)
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
        course = self.get_object(pk)
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
        course = self.get_object(pk)
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
        course = self.get_object(pk)
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
    queryset = CourseAllocation.objects.all()
    serializer_class = CourseAllocationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['lecturer', 'semester']
    search_fields = ['lecturer__first_name', 'lecturer__last_name', 'lecturer__email', 'courses__title', 'courses__code']
    ordering_fields = ['lecturer__first_name', 'lecturer__last_name']
    ordering = ['lecturer__first_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация для преподавателей - только свои назначения
        if self.request.user.is_lecturer:
            queryset = queryset.filter(lecturer=self.request.user)
        
        # Предзагрузка связанных данных для оптимизации
        queryset = queryset.select_related('lecturer').prefetch_related('courses')
        
        return queryset

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