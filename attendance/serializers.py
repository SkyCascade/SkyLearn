from rest_framework import serializers
from .models import ScheduleItem, Attendance
from accounts.models import Student, Group
from course.models import Course


class ScheduleItemSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для расписания"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = ScheduleItem
        fields = [
            'id', 'course', 'course_title', 'course_code', 
            'group', 'group_name', 'order', 'day', 'start', 'end'
        ]


class StudentScheduleItemSerializer(serializers.ModelSerializer):
    """Сериализатор расписания для студентов (только чтение)"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    lecturer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduleItem
        fields = [
            'id', 'course', 'course_title', 'course_code', 
            'group', 'group_name', 'lecturer_name', 'order', 'day', 'start', 'end'
        ]
        read_only_fields = ['id', 'course', 'group', 'order', 'day', 'start', 'end']
    
    def get_lecturer_name(self, obj):
        # Предполагая, что у Course есть связь с преподавателем
        if hasattr(obj.course, 'allocated_course'):
            allocated = obj.course.allocated_course.first()
            if allocated and allocated.lecturer:
                return allocated.lecturer.get_full_name
        return None


class LecturerScheduleItemSerializer(serializers.ModelSerializer):
    """Сериализатор расписания для преподавателей"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = ScheduleItem
        fields = [
            'id', 'course', 'course_title', 'course_code', 
            'group', 'group_name', 'order', 'day', 'start', 'end'
        ]
        read_only_fields = ['id', 'course_title', 'course_code', 'group_name']


class AdminScheduleItemSerializer(serializers.ModelSerializer):
    """Сериализатор расписания для администраторов (полный доступ)"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = ScheduleItem
        fields = [
            'id', 'course', 'course_title', 'course_code', 
            'group', 'group_name', 'order', 'day', 'start', 'end'
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для посещаемости"""
    student_name = serializers.CharField(source='Student.get_full_name', read_only=True)
    student_id = serializers.IntegerField(source='Student.id', read_only=True)
    schedule_day = serializers.CharField(source='shcedule.day', read_only=True)
    schedule_time = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='shcedule.course.title', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'Student', 'student_name', 'student_id', 
            'status', 'shcedule', 'schedule_day', 'schedule_time', 'course_title'
        ]
    
    def get_schedule_time(self, obj):
        if obj.shcedule:
            return f"{obj.shcedule.start.strftime('%H:%M')} - {obj.shcedule.end.strftime('%H:%M')}"
        return None


class StudentAttendanceSerializer(serializers.ModelSerializer):
    """Сериализатор посещаемости для студентов (только чтение)"""
    schedule_day = serializers.CharField(source='shcedule.day', read_only=True)
    schedule_time = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='shcedule.course.title', read_only=True)
    course_code = serializers.CharField(source='shcedule.course.code', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'status', 'shcedule', 'schedule_day', 
            'schedule_time', 'course_title', 'course_code'
        ]
        read_only_fields = ['id', 'status', 'shcedule']
    
    def get_schedule_time(self, obj):
        if obj.shcedule:
            return f"{obj.shcedule.start.strftime('%H:%M')} - {obj.shcedule.end.strftime('%H:%M')}"
        return None


class LecturerAttendanceSerializer(serializers.ModelSerializer):
    """Сериализатор посещаемости для преподавателей (можно редактировать)"""
    student_name = serializers.CharField(source='Student.get_full_name', read_only=True)
    student_id = serializers.IntegerField(source='Student.id', read_only=True)
    schedule_day = serializers.CharField(source='shcedule.day', read_only=True)
    schedule_time = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='shcedule.course.title', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'Student', 'student_name', 'student_id', 
            'status', 'shcedule', 'schedule_day', 'schedule_time', 'course_title'
        ]
        read_only_fields = ['Student', 'shcedule']
    
    def get_schedule_time(self, obj):
        if obj.shcedule:
            return f"{obj.shcedule.start.strftime('%H:%M')} - {obj.shcedule.end.strftime('%H:%M')}"
        return None


class AdminAttendanceSerializer(serializers.ModelSerializer):
    """Сериализатор посещаемости для администраторов (полный доступ)"""
    student_name = serializers.CharField(source='Student.get_full_name', read_only=True)
    schedule_day = serializers.CharField(source='shcedule.day', read_only=True)
    schedule_time = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='shcedule.course.title', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'Student', 'student_name', 
            'status', 'shcedule', 'schedule_day', 'schedule_time', 'course_title'
        ]
    
    def get_schedule_time(self, obj):
        if obj.shcedule:
            return f"{obj.shcedule.start.strftime('%H:%M')} - {obj.shcedule.end.strftime('%H:%M')}"
        return None


class BulkAttendanceUpdateSerializer(serializers.Serializer):
    """Сериализатор для массового обновления посещаемости"""
    student_id = serializers.IntegerField()
    status = serializers.BooleanField()


class BulkAttendancesUpdateSerializer(serializers.Serializer):
    """Сериализатор для массового обновления посещаемости по расписанию"""
    schedule_id = serializers.IntegerField()
    attendances = BulkAttendanceUpdateSerializer(many=True)
    
    def validate(self, data):
        return data
