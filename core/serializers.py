from rest_framework import serializers
from .models import NewsAndEvents, Session, Semester, SEMESTER, ActivityLog
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


class SessionSerializer(serializers.ModelSerializer):
    next_session_begins = serializers.DateField(required=True)

    class Meta:
        model = Session
        fields = ["session", "is_current_session", "next_session_begins"]

    def validate_session(self, value):
        """
        Validate session field
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Session cannot be empty")
        
        # Check for uniqueness
        if Session.objects.filter(session=value).exists():
            if self.instance is None or self.instance.session != value:
                raise serializers.ValidationError("A session with this name already exists")
        
        return value.strip()

    def validate_next_session_begins(self, value):
        """
        Validate next_session_begins field
        """
        if not value:
            raise serializers.ValidationError("Next session begins date is required")
        return value


class SessionDetailSerializer(serializers.ModelSerializer):
    next_session_begins = serializers.DateField(format="%Y-%m-%d")
    semesters = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = ["id", "session", "is_current_session", "next_session_begins", "semesters"]
    
    def get_semesters(self, obj):
        return SemesterSerializer(obj.semester_set.all(), many=True).data


# serializers.py - Updated SemesterSerializer

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
    
    session = serializers.PrimaryKeyRelatedField(
        queryset=Session.objects.all(),
        required=True
    )
    
    next_semester_begins = serializers.DateField(required=True)

    class Meta:
        model = Semester
        fields = ["semester", "is_current_semester", "session", "next_semester_begins"]

    def validate(self, data):
        """
        Проверка, что может быть только один текущий семестр
        """
        is_current_semester = data.get('is_current_semester', False)
        
        if is_current_semester:
            current_semesters = Semester.objects.filter(is_current_semester=True)
            if self.instance:
                current_semesters = current_semesters.exclude(pk=self.instance.pk)
            
            if current_semesters.exists():
                raise serializers.ValidationError({
                    "is_current_semester": "There can only be one current semester"
                })
        
        # Проверка, что next_semester_begins после даты начала сессии
        session = data.get('session')
        next_semester_begins = data.get('next_semester_begins')
        
        if session and next_semester_begins:
            # Get the session instance to access next_session_begins
            session_instance = Session.objects.get(pk=session.pk)
            if session_instance.next_session_begins:
                if next_semester_begins <= session_instance.next_session_begins:
                    raise serializers.ValidationError({
                        "next_semester_begins": "Next semester must begin after the session start date"
                    })
        
        return data

    def to_representation(self, instance):
        """
        Переопределение для красивого отображения данных
        """
        representation = super().to_representation(instance)
        representation['session'] = {
            'id': instance.session.id,
            'session': instance.session.session
        }
        representation['next_semester_begins'] = instance.next_semester_begins.strftime("%Y-%m-%d") if instance.next_semester_begins else None
        return representation

class SemesterDetailSerializer(serializers.ModelSerializer):
    session_info = serializers.SerializerMethodField()
    next_semester_begins = serializers.DateField(format="%Y-%m-%d")
    
    class Meta:
        model = Semester
        fields = ["id", "semester", "is_current_semester", "session", "session_info", "next_semester_begins"]
    
    def get_session_info(self, obj):
        return {
            'id': obj.session.id,
            'session': obj.session.session,
            'is_current_session': obj.session.is_current_session
        }


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