from rest_framework import serializers
from .models import  Course
from django.utils.translation import gettext_lazy as _
from .models import CourseAllocation, Course
from django.contrib.auth import get_user_model


    
class CourseSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.title', read_only=True)
    is_current_semester = serializers.BooleanField(read_only=True)
    absolute_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ['slug', 'is_current_semester']
        extra_kwargs = {
            'program': {'write_only': True}
        }

    def get_absolute_url(self, obj):
        try:
            request = self.context.get('request')
            if request and hasattr(obj, 'get_absolute_url'):
                return request.build_absolute_uri(obj.get_absolute_url())
        except Exception:
            # Return None if URL reversal fails
            return None
        return None

    def validate_code(self, value):
        """Проверка уникальности кода курса"""
        if self.instance and self.instance.code == value:
            return value
            
        if Course.objects.filter(code=value).exists():
            raise serializers.ValidationError(_("A course with this code already exists."))
        return value

    def validate_credit(self, value):
        """Проверка что кредиты не отрицательные"""
        if value < 0:
            raise serializers.ValidationError(_("Credit cannot be negative."))
        return value

    def validate_year(self, value):
        """Проверка корректности года"""
        from django.conf import settings
        valid_years = [choice[0] for choice in settings.YEARS]
        if value not in valid_years:
            raise serializers.ValidationError(_("Invalid year value."))
        return value

    def validate_semester(self, value):
        """Проверка корректности семестра"""
        from django.conf import settings
        valid_semesters = [choice[0] for choice in settings.SEMESTER_CHOICES]
        if value not in valid_semesters:
            raise serializers.ValidationError(_("Invalid semester value."))
        return value
    
    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get('admin') or self.context.get('request').user
        validated_data['admin'] = admin
        return super().create(validated_data)




User = get_user_model()

class CourseAllocationSerializer(serializers.ModelSerializer):
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)
    lecturer_email = serializers.CharField(source='lecturer.email', read_only=True)
    courses_details = serializers.SerializerMethodField(read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = CourseAllocation
        fields = [
            'id', 'lecturer', 'lecturer_name', 'lecturer_email', 
            'courses', 'courses_details', 'semester', 'semester_name',
            'group', 'group_name'
        ]
        extra_kwargs = {
            'courses': {'write_only': True},
        }

    def get_courses_details(self, obj):
        return [
            {
                'id': course.id,
                'title': course.title,
                'code': course.code,
                'credit': course.credit,
                'level': course.level
            }
            for course in obj.courses.all()
        ]

    def validate(self, data):
        # Проверка, что пользователь является преподавателем
        lecturer = data.get('lecturer')
        if lecturer and not lecturer.is_lecturer:
            raise serializers.ValidationError(
                "Selected user must be a lecturer"
            )
        
        # Проверка, что курсы не пустые
        courses = data.get('courses', [])
        if not courses:
            raise serializers.ValidationError(
                "At least one course must be selected"
            )
        
        return data

    def create(self, validated_data):
        courses = validated_data.pop('courses', [])
        # Автоматически устанавливаем admin из контекста
        admin = self.context.get('admin') or self.context.get('request').user
        validated_data['admin'] = admin
        
        allocation = CourseAllocation.objects.create(**validated_data)
        allocation.courses.set(courses)
        
        # После сохранения сработает сигнал в приложении result,
        # который автоматически создаст записи оценок для всех студентов в группе
        return allocation

    def update(self, instance, validated_data):
        courses = validated_data.pop('courses', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if courses is not None:
            instance.courses.set(courses)
        
        return instance

    

class StudentCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAllocation
        fields = ['id', 'lecturer', 'courses', 'semester', 'group']
