from rest_framework import serializers
from .models import NewsAndEvents, Semester, SEMESTER, ActivityLog
from django.contrib.auth import get_user_model

User = get_user_model()

class NewsAndEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsAndEvents
        fields = ("title", "summary", "posted_as")

    def validate_title(self, value):
        """
        Валидация для поля title
        """
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value

    def validate_summary(self, value):
        """
        Валидация для поля summary
        """
        if not value.strip():
            raise serializers.ValidationError("Summary cannot be empty")
        return value
    
    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get('admin') or self.context.get('request').user
        validated_data['admin'] = admin
        return super().create(validated_data)


class SemesterSerializer(serializers.ModelSerializer):
    semester = serializers.ChoiceField(
        choices=SEMESTER,
        label="semester"
    )
    
    is_current_semester = serializers.BooleanField(
        label="is current semester ?",
        required=False,
        default=False
    )
    
    next_semester_begins = serializers.DateField(required=True)

    class Meta:
        model = Semester
        fields = ["semester", "is_current_semester", "next_semester_begins"]

    def validate(self, data):
        """
        Проверка, что может быть только один текущий семестр для данного администратора
        """
        is_current_semester = data.get('is_current_semester', False)
        
        if is_current_semester:
            # Получаем admin из контекста (будет передан из view)
            admin = self.context.get('admin') or self.context.get('request').user
            
            current_semesters = Semester.objects.filter(
                is_current_semester=True,
                admin=admin
            )
            
            if self.instance:
                current_semesters = current_semesters.exclude(pk=self.instance.pk)
            
            if current_semesters.exists():
                raise serializers.ValidationError({
                    "is_current_semester": "There can only be one current semester"
                })
        
        return data
    
    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get('admin') or self.context.get('request').user
        validated_data['admin'] = admin
        return super().create(validated_data)


class SemesterDetailSerializer(serializers.ModelSerializer):
    next_semester_begins = serializers.DateField(format="%Y-%m-%d")
    
    class Meta:
        model = Semester
        fields = ["id", "semester", "is_current_semester", "next_semester_begins"]


class NewsAndEventsDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = NewsAndEvents
        fields = ("id", "title", "summary", "posted_as", "created_at", "updated_at")


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'message', 'created_at']


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    student_count = serializers.IntegerField()
    lecturer_count = serializers.IntegerField()
    superuser_count = serializers.IntegerField()
    males_count = serializers.IntegerField()
    females_count = serializers.IntegerField()
    logs = ActivityLogSerializer(many=True)


class HomeSerializer(serializers.Serializer):
    """Serializer for home page data"""
    title = serializers.CharField(default="News & Events")
    items = serializers.ListField(child=serializers.DictField())