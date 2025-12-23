from rest_framework import serializers
from .models import  Program, Semester, SEMESTER
from course.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()


### program serializers

class ProgramListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ["id", "name"]

    def get_name(self, obj):
        return obj.get_name(self.context.get('lang', 'ru'))
    
class ProgramWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["name_ru", "name_en", "name_kg"]

    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get('admin')
        program = Program.objects.create(admin=admin, **validated_data)
        return program
    
    def update(self, instance, validated_data):
        """
        Автоматически устанавливаем не трогая админ
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

### semester serializers


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ["__all__"]

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["__all__"]

class SemesterListSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)

    class Meta:
        model = Semester
        fields = ["id", "name", "is_current", "academic_year", "courses"]

class SemesterWriteSerializer(serializers.ModelSerializer):
    name = serializers.ChoiceField(
        choices=SEMESTER,
        label="semester"
    )
    
    is_current = serializers.BooleanField(
        label="is current semester ?",
        required=False,
    )
        
    class Meta:
        model = Semester
        fields = ["name", "is_current", "courses", "academic_year"]

    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get('admin')
        courses = validated_data.pop('courses', [])
        
        semester = Semester.objects.create(admin=admin, **validated_data)
        semester.courses.set(courses)
        return semester

    def update(self, instance, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        courses = validated_data.pop('courses', serializers.empty)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if courses is not serializers.empty:
            instance.courses.set(courses)
        return instance


class SemesterDetailSerializer(serializers.ModelSerializer):
    next_semester_begins = serializers.DateField(format="%Y-%m-%d")
    
    class Meta:
        model = Semester
        fields = ["id", "name", "is_current", "courses", "academic_year"]


