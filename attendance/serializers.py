from rest_framework import serializers

from .models import Attendance, LessonTime, ScheduleItem


class LessonTimeSerializer(serializers.ModelSerializer):
    """Сериализатор для времен уроков"""

    class Meta:
        model = LessonTime
        fields = ["id", "order", "start_time", "end_time"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get("admin") or self.context.get("request").user
        validated_data["admin"] = admin
        return super().create(validated_data)


class ScheduleItemSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для расписания"""

    course_title = serializers.CharField(source="course.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    lesson_order = serializers.IntegerField(source="lesson_time.order", read_only=True)
    start_time = serializers.TimeField(source="lesson_time.start_time", read_only=True)
    end_time = serializers.TimeField(source="lesson_time.end_time", read_only=True)

    class Meta:
        model = ScheduleItem
        fields = [
            "id",
            "course",
            "course_title",
            "group",
            "group_name",
            "lesson_time",
            "lesson_order",
            "day",
            "date",
            "start_time",
            "end_time",
        ]

    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get("admin") or self.context.get("request").user
        validated_data["admin"] = admin
        return super().create(validated_data)


class StudentScheduleItemSerializer(serializers.ModelSerializer):
    """Сериализатор расписания для студентов (только чтение)"""

    course_title = serializers.CharField(source="course.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    lecturer_name = serializers.SerializerMethodField()
    lesson_order = serializers.IntegerField(source="lesson_time.order", read_only=True)
    start_time = serializers.TimeField(source="lesson_time.start_time", read_only=True)
    end_time = serializers.TimeField(source="lesson_time.end_time", read_only=True)

    class Meta:
        model = ScheduleItem
        fields = [
            "id",
            "course",
            "course_title",
            "course_code",
            "group",
            "group_name",
            "lecturer_name",
            "lesson_order",
            "day",
            "date",
            "start_time",
            "end_time",
        ]
        read_only_fields = [
            "id",
            "course",
            "group",
            "lesson_order",
            "day",
            "date",
            "start_time",
            "end_time",
        ]

    def get_lecturer_name(self, obj):
        # Предполагая, что у Course есть связь с преподавателем
        if hasattr(obj.course, "allocated_course"):
            allocated = obj.course.allocated_course.first()
            if allocated and allocated.lecturer:
                return allocated.lecturer.get_full_name
        return None


class LecturerScheduleItemSerializer(serializers.ModelSerializer):
    """Сериализатор расписания для преподавателей"""

    course_title = serializers.CharField(source="course.name", read_only=True)

    group_name = serializers.CharField(source="group.name", read_only=True)
    lesson_order = serializers.IntegerField(source="lesson_time.order", read_only=True)
    start_time = serializers.TimeField(source="lesson_time.start_time", read_only=True)
    end_time = serializers.TimeField(source="lesson_time.end_time", read_only=True)

    class Meta:
        model = ScheduleItem
        fields = [
            "id",
            "course",
            "course_title",
            "group",
            "group_name",
            "lesson_order",
            "day",
            "date",
            "start_time",
            "end_time",
        ]
        read_only_fields = ["id", "course_title", "group_name"]


class AdminScheduleItemSerializer(serializers.ModelSerializer):
    """Сериализатор расписания для администраторов (полный доступ)"""

    course_title = serializers.CharField(source="course.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    lesson_order = serializers.IntegerField(source="lesson_time.order", read_only=True)
    start_time = serializers.TimeField(source="lesson_time.start_time", read_only=True)
    end_time = serializers.TimeField(source="lesson_time.end_time", read_only=True)

    class Meta:
        model = ScheduleItem
        fields = [
            "id",
            "course",
            "course_title",
            "group",
            "group_name",
            "lesson_time",
            "lesson_order",
            "day",
            "date",
            "start_time",
            "end_time",
        ]

    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get("admin") or self.context.get("request").user
        validated_data["admin"] = admin
        return super().create(validated_data)


class AttendanceSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для посещаемости"""

    student_name = serializers.CharField(source="Student.get_full_name", read_only=True)
    student_id = serializers.IntegerField(source="Student.id", read_only=True)
    schedule_day = serializers.CharField(source="shcedule.day", read_only=True)
    schedule_date = serializers.DateField(source="shcedule.date", read_only=True)
    schedule_time = serializers.SerializerMethodField()
    course_title = serializers.CharField(source="shcedule.course.title", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "Student",
            "student_name",
            "student_id",
            "status",
            "shcedule",
            "schedule_day",
            "schedule_date",
            "schedule_time",
            "course_title",
        ]

    def get_schedule_time(self, obj):
        if obj.shcedule and obj.shcedule.lesson_time:
            return f"{obj.shcedule.lesson_time.start_time.strftime('%H:%M')} - {obj.shcedule.lesson_time.end_time.strftime('%H:%M')}"
        return None


class StudentAttendanceSerializer(serializers.ModelSerializer):
    """Сериализатор посещаемости для студентов (только чтение)"""

    schedule_day = serializers.CharField(source="shcedule.day", read_only=True)
    schedule_date = serializers.DateField(source="shcedule.date", read_only=True)
    schedule_time = serializers.SerializerMethodField()
    course_title = serializers.CharField(source="shcedule.course.title", read_only=True)
    course_code = serializers.CharField(source="shcedule.course.code", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "status",
            "shcedule",
            "schedule_day",
            "schedule_date",
            "schedule_time",
            "course_title",
            "course_code",
        ]
        read_only_fields = ["id", "status", "shcedule"]

    def get_schedule_time(self, obj):
        if obj.shcedule and obj.shcedule.lesson_time:
            return f"{obj.shcedule.lesson_time.start_time.strftime('%H:%M')} - {obj.shcedule.lesson_time.end_time.strftime('%H:%M')}"
        return None


class LecturerAttendanceSerializer(serializers.ModelSerializer):
    """Сериализатор посещаемости для преподавателей (можно редактировать)"""

    student_name = serializers.CharField(source="Student.get_full_name", read_only=True)
    student_id = serializers.IntegerField(source="Student.id", read_only=True)
    schedule_day = serializers.CharField(source="shcedule.day", read_only=True)
    schedule_date = serializers.DateField(source="shcedule.date", read_only=True)
    schedule_time = serializers.SerializerMethodField()
    course_title = serializers.CharField(source="shcedule.course.title", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "Student",
            "student_name",
            "student_id",
            "status",
            "shcedule",
            "schedule_day",
            "schedule_date",
            "schedule_time",
            "course_title",
        ]
        read_only_fields = ["Student", "shcedule"]

    def get_schedule_time(self, obj):
        if obj.shcedule and obj.shcedule.lesson_time:
            return f"{obj.shcedule.lesson_time.start_time.strftime('%H:%M')} - {obj.shcedule.lesson_time.end_time.strftime('%H:%M')}"
        return None


class AdminAttendanceSerializer(serializers.ModelSerializer):
    """Сериализатор посещаемости для администраторов (полный доступ)"""

    student_name = serializers.CharField(source="Student.get_full_name", read_only=True)
    schedule_day = serializers.CharField(source="shcedule.day", read_only=True)
    schedule_date = serializers.DateField(source="shcedule.date", read_only=True)
    schedule_time = serializers.SerializerMethodField()
    course_title = serializers.CharField(source="shcedule.course.title", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "Student",
            "student_name",
            "status",
            "shcedule",
            "schedule_day",
            "schedule_date",
            "schedule_time",
            "course_title",
        ]

    def get_schedule_time(self, obj):
        if obj.shcedule and obj.shcedule.lesson_time:
            return f"{obj.shcedule.lesson_time.start_time.strftime('%H:%M')} - {obj.shcedule.lesson_time.end_time.strftime('%H:%M')}"
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
