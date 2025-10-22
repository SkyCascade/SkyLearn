# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import TakenCourse, Result
from .serializers import (
    TakenCourseSerializer, 
    ResultSerializer,
    StudentResultSerializer,
    GradeCalculationSerializer
)
from accounts.models import Student
from course.models import Course

class TakenCourseViewSet(viewsets.ModelViewSet):
    queryset = TakenCourse.objects.all()
    serializer_class = TakenCourseSerializer 
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация для студентов - только свои курсы
        if hasattr(self.request.user, 'student'):
            return queryset.filter(student=self.request.user.student)
        
        # Фильтрация для преподавателей/администраторов
        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')
        semester = self.request.query_params.get('semester')
        level = self.request.query_params.get('level')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if semester:
            queryset = queryset.filter(course__semester=semester)
        if level:
            queryset = queryset.filter(course__level=level)
            
        return queryset
    
    def perform_create(self, serializer):
        # Автоматически рассчитываем итоговые значения при создании
        instance = serializer.save()
        instance.save()  # Это вызовет метод save() модели с пересчетом total, grade и comment
    
    def perform_update(self, serializer):
        # Автоматически пересчитываем итоговые значения при обновлении
        instance = serializer.save()
        instance.save()  # Это вызовет метод save() модели с пересчетом total, grade и comment
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Создание нескольких записей TakenCourse одновременно"""
        data = request.data
        if not isinstance(data, list):
            return Response(
                {"error": "Expected a list of items"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_items = []
        errors = []
        
        for item_data in data:
            serializer = self.get_serializer(data=item_data)
            if serializer.is_valid():
                instance = serializer.save()
                instance.save()  # Пересчет итоговых значений
                created_items.append(serializer.data)
            else:
                errors.append({
                    'data': item_data,
                    'errors': serializer.errors
                })
        
        if errors:
            return Response(
                {
                    'created': created_items,
                    'errors': errors
                },
                status=status.HTTP_207_MULTI_STATUS
            )
        
        return Response(created_items, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def student_courses(self, request):
        """Получить курсы конкретного студента"""
        student_id = request.query_params.get('student_id')
        semester = request.query_params.get('semester')
        level = request.query_params.get('level')
        
        if not student_id:
            return Response(
                {"error": "student_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(student_id=student_id)
        
        if semester:
            queryset = queryset.filter(course__semester=semester)
        if level:
            queryset = queryset.filter(course__level=level)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def calculate_grade(self, request):
        """Рассчитать оценку на основе входных данных"""
        serializer = GradeCalculationSerializer(data=request.data)
        if serializer.is_valid():
            # Создаем временный объект для расчета
            temp_course = TakenCourse(
                assignment=serializer.validated_data['assignment'],
                mid_exam=serializer.validated_data['mid_exam'],
                attendance=serializer.validated_data['attendance'],
                final_exam=serializer.validated_data['final_exam']
            )
            
            response_data = {
                'assignment': temp_course.assignment,
                'mid_exam': temp_course.mid_exam,
                'attendance': temp_course.attendance,
                'final_exam': temp_course.final_exam,
                'total': temp_course.get_total(),
                'grade': temp_course.get_grade(),
                'comment': temp_course.get_comment(),
                'point': temp_course.get_point()
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация для студентов - только свои результаты
        if hasattr(self.request.user, 'student'):
            return queryset.filter(student=self.request.user.student)
        
        # Фильтрация для преподавателей/администраторов
        student_id = self.request.query_params.get('student_id')
        semester = self.request.query_params.get('semester')
        level = self.request.query_params.get('level')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if semester:
            queryset = queryset.filter(semester=semester)
        if level:
            queryset = queryset.filter(level=level)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def generate_result(self, request):
        """Сгенерировать результат для студента за семестр"""
        serializer = StudentResultSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data['student']
            semester = serializer.validated_data['semester']
            level = serializer.validated_data['level']
            
            # Получаем все курсы студента за указанный семестр и уровень
            taken_courses = TakenCourse.objects.filter(
                student=student,
                course__semester=semester,
                course__level=level
            )
            
            if not taken_courses.exists():
                return Response(
                    {"error": "No courses found for this student in the specified semester and level"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Рассчитываем GPA и CGPA
            total_points = sum(tc.point for tc in taken_courses)
            total_credits = sum(tc.course.credit for tc in taken_courses)
            
            if total_credits > 0:
                gpa = round(total_points / total_credits, 2)
            else:
                gpa = 0.0
            
            # Рассчитываем CGPA (все курсы студента)
            all_taken_courses = TakenCourse.objects.filter(student=student)
            all_total_points = sum(tc.point for tc in all_taken_courses)
            all_total_credits = sum(tc.course.credit for tc in all_taken_courses)
            
            if all_total_credits > 0:
                cgpa = round(all_total_points / all_total_credits, 2)
            else:
                cgpa = 0.0
            
            # Создаем или обновляем запись Result
            result, created = Result.objects.update_or_create(
                student=student,
                semester=semester,
                level=level,
                defaults={
                    'gpa': gpa,
                    'cgpa': cgpa,
                    'session': f"{semester} Session"  # Можно настроить под вашу логику
                }
            )
            
            result_serializer = ResultSerializer(result)
            return Response(result_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def student_results(self, request):
        """Получить все результаты конкретного студента"""
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {"error": "student_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(student_id=student_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def semester_results(self, request):
        """Получить результаты всех студентов за определенный семестр и уровень"""
        semester = request.query_params.get('semester')
        level = request.query_params.get('level')
        
        if not semester or not level:
            return Response(
                {"error": "semester and level parameters are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(semester=semester, level=level)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)