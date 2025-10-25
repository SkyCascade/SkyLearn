from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Grade_1st_module, Grade_2nd_module, Grade_semester
from .serializers import (
    StudentGrade1stModuleSerializer, 
    StudentGrade2ndModuleSerializer, 
    StudentGradeSemesterSerializer,
    LecturerGrade1stModuleSerializer,
    LecturerGrade2ndModuleSerializer,
    LecturerGradeSemesterSerializer,
    BulkGradesUpdateSerializer
)

class Grade1stModuleViewSet(viewsets.ModelViewSet):
    queryset = Grade_1st_module.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['lecturer', 'student', 'course', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'course__title', 'course__code']
    ordering_fields = ['student', 'course', 'total']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_lecturer:
            queryset = queryset.filter(lecturer=self.request.user)
        elif hasattr(self.request.user, 'student'):
            queryset = queryset.filter(student=self.request.user.student)
        return queryset

    def get_serializer_class(self):
        if self.request.user.is_lecturer:
            return LecturerGrade1stModuleSerializer
        return StudentGrade1stModuleSerializer

    def get_permissions(self):
        if hasattr(self.request.user, 'student') and self.request.method not in ['GET', 'HEAD', 'OPTIONS']:
            from rest_framework.permissions import IsAdminUser
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)')
    def by_course(self, request, course_id=None):
        """Получить оценки по конкретному курсу"""
        queryset = self.get_queryset().filter(course_id=course_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class Grade2ndModuleViewSet(viewsets.ModelViewSet):
    queryset = Grade_2nd_module.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['lecturer', 'student', 'course', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'course__title', 'course__code']
    ordering_fields = ['student', 'course', 'total']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_lecturer:
            queryset = queryset.filter(lecturer=self.request.user)
        elif hasattr(self.request.user, 'student'):
            queryset = queryset.filter(student=self.request.user.student)
        return queryset

    def get_serializer_class(self):
        if self.request.user.is_lecturer:
            return LecturerGrade2ndModuleSerializer
        return StudentGrade2ndModuleSerializer

    def get_permissions(self):
        if hasattr(self.request.user, 'student') and self.request.method not in ['GET', 'HEAD', 'OPTIONS']:
            from rest_framework.permissions import IsAdminUser
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)')
    def by_course(self, request, course_id=None):
        """Получить оценки по конкретному курсу"""
        queryset = self.get_queryset().filter(course_id=course_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class GradeSemesterViewSet(viewsets.ModelViewSet):
    queryset = Grade_semester.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['lecturer', 'student', 'course', 'semester', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'course__title', 'course__code']
    ordering_fields = ['student', 'course', 'total', 'semester']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_lecturer:
            queryset = queryset.filter(lecturer=self.request.user)
        elif hasattr(self.request.user, 'student'):
            queryset = queryset.filter(student=self.request.user.student)
        return queryset

    def get_serializer_class(self):
        if self.request.user.is_lecturer:
            return LecturerGradeSemesterSerializer
        return StudentGradeSemesterSerializer

    def get_permissions(self):
        if hasattr(self.request.user, 'student') and self.request.method not in ['GET', 'HEAD', 'OPTIONS']:
            from rest_framework.permissions import IsAdminUser
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)')
    def by_course(self, request, course_id=None):
        """Получить оценки по конкретному курсу"""
        queryset = self.get_queryset().filter(course_id=course_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_grades(self, request):
        """Получить все оценки текущего студента"""
        if not hasattr(request.user, 'student'):
            return Response(
                {"detail": "Only students can view their grades"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        grades = self.get_queryset().filter(student=request.user.student)
        serializer = self.get_serializer(grades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_all_grades(self, request):
        """Получить все оценки студента (все модули)"""
        if not hasattr(request.user, 'student'):
            return Response(
                {"detail": "Only students can view their grades"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student
        
        grade_1st = Grade_1st_module.objects.filter(student=student)
        grade_2nd = Grade_2nd_module.objects.filter(student=student)
        grade_semester = Grade_semester.objects.filter(student=student)
        
        data = {
            'first_module_grades': StudentGrade1stModuleSerializer(grade_1st, many=True).data,
            'second_module_grades': StudentGrade2ndModuleSerializer(grade_2nd, many=True).data,
            'semester_grades': StudentGradeSemesterSerializer(grade_semester, many=True).data,
        }
        
        return Response(data)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Grade_1st_module, Grade_2nd_module, Grade_semester
from .serializers import (
    StudentGrade1stModuleSerializer, 
    StudentGrade2ndModuleSerializer, 
    StudentGradeSemesterSerializer,
    LecturerGrade1stModuleSerializer,
    LecturerGrade2ndModuleSerializer,
    LecturerGradeSemesterSerializer,
    BulkGradesUpdateSerializer
)

# ... остальные ViewSets остаются без изменений ...

class LecturerBulkGradesViewSet(viewsets.ViewSet):
    """ViewSet для массового обновления оценок преподавателями"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='bulk-update')
    def bulk_update(self, request):
        """Массовое обновление оценок для нескольких студентов"""
        if not request.user.is_lecturer:
            return Response(
                {"detail": "Only lecturers can update grades"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = BulkGradesUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        course_id = serializer.validated_data['course_id']
        grade_type = serializer.validated_data['grade_type']
        grades_data = serializer.validated_data['grades']

        # Определяем модель в зависимости от типа оценок
        if grade_type == '1st_module':
            model = Grade_1st_module
        elif grade_type == '2nd_module':
            model = Grade_2nd_module
        else:  # semester
            model = Grade_semester

        try:
            with transaction.atomic():
                updated_grades = []
                
                for grade_data in grades_data:
                    student_id = grade_data['student_id']
                    
                    # Получаем объект оценки
                    grade_obj = model.objects.get(
                        lecturer=request.user,
                        course_id=course_id,
                        student_id=student_id
                    )
                    
                    # Обновляем поля
                    update_fields = []
                    if 'attendance' in grade_data:
                        grade_obj.attendance = grade_data['attendance']
                        update_fields.append('attendance')
                    if 'activities' in grade_data:
                        grade_obj.activities = grade_data['activities']
                        update_fields.append('activities')
                    if 'exam' in grade_data:
                        grade_obj.exam = grade_data['exam']
                        update_fields.append('exam')
                    
                    # Пересчитываем total и сохраняем
                    if update_fields:
                        grade_obj.total = grade_obj.attendance + grade_obj.activities + grade_obj.exam
                        update_fields.append('total')
                        grade_obj.save(update_fields=update_fields)
                        
                        updated_grades.append({
                            'student_id': student_id,
                            'student_name': grade_obj.student.get_full_name(),
                            'attendance': grade_obj.attendance,
                            'activities': grade_obj.activities,
                            'exam': grade_obj.exam,
                            'total': grade_obj.total
                        })
                
                return Response({
                    'detail': f'Successfully updated {len(updated_grades)} grades',
                    'updated_grades': updated_grades
                })
                
        except model.DoesNotExist:
            return Response(
                {"detail": "Grade record not found for one of the students"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Error updating grades: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class LecturerCourseGradesViewSet(viewsets.ViewSet):
    """ViewSet для получения оценок студентов по курсу"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='course-grades')
    def course_grades(self, request):
        """Получить всех студентов и их оценки по конкретному курсу"""
        if not request.user.is_lecturer:
            return Response(
                {"detail": "Only lecturers can view course grades"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {"detail": "course_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            grade_1st = Grade_1st_module.objects.filter(
                lecturer=request.user, 
                course_id=course_id
            ).select_related('student', 'course')
            
            grade_2nd = Grade_2nd_module.objects.filter(
                lecturer=request.user, 
                course_id=course_id
            ).select_related('student', 'course')
            
            grade_semester = Grade_semester.objects.filter(
                lecturer=request.user, 
                course_id=course_id
            ).select_related('student', 'course')

            data = {
                'first_module': LecturerGrade1stModuleSerializer(grade_1st, many=True).data,
                'second_module': LecturerGrade2ndModuleSerializer(grade_2nd, many=True).data,
                'semester': LecturerGradeSemesterSerializer(grade_semester, many=True).data,
            }
            
            return Response(data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error retrieving grades: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )