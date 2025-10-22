# serializers.py
from rest_framework import serializers
from .models import TakenCourse, Result
from accounts.models import Student
from course.models import Course

class TakenCourseSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matric_number = serializers.CharField(source='student.matric_number', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_credit = serializers.IntegerField(source='course.credit', read_only=True)
    
    class Meta:
        model = TakenCourse
        fields = [
            'id', 'student', 'student_name', 'student_matric_number',
            'course', 'course_title', 'course_code', 'course_credit',
            'assignment', 'mid_exam', 'attendance', 'final_exam',
            'total', 'grade', 'comment'
        ]
        read_only_fields = ['total', 'grade', 'comment']

class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matric_number = serializers.CharField(source='student.matric_number', read_only=True)
    
    class Meta:
        model = Result
        fields = [
            'id', 'student', 'student_name', 'student_matric_number',
            'gpa', 'cgpa', 'semester', 'session', 'level'
        ]

class StudentResultSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    semester = serializers.CharField(max_length=100)
    level = serializers.CharField(max_length=25)
    
    def validate(self, data):
        student = data['student']
        semester = data['semester']
        level = data['level']
        
        # Проверяем, есть ли курсы для этого студента в указанном семестре и уровне
        taken_courses = TakenCourse.objects.filter(
            student=student,
            course__semester=semester,
            course__level=level
        )
        
        if not taken_courses.exists():
            raise serializers.ValidationError(
                "No courses found for this student in the specified semester and level"
            )
        
        return data

class GradeCalculationSerializer(serializers.Serializer):
    assignment = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    mid_exam = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    attendance = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    final_exam = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    
    total = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    grade = serializers.CharField(max_length=2, read_only=True)
    comment = serializers.CharField(max_length=200, read_only=True)