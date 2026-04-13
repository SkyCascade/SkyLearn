from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AcademicYear, Course, CourseAllocation, Module, Program, Semester

User = get_user_model()


### program serializers


class ProgramListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "name"]


class ProgramWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["name"]

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
    program = ProgramListSerializer()

    class Meta:
        model = AcademicYear
        fields = ["id", "year", "program", "is_current"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class SemesterListSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)

    class Meta:
        model = Semester
        fields = ["id", "name", "is_current", "academic_year", "courses"]


class SemesterWriteSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), many=True, required=False
    )
    is_current = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Semester
        fields = ["name", "is_current", "courses", "academic_year"]

    def create(self, validated_data):
        """
        Автоматически устанавливаем admin из контекста
        """
        admin = self.context.get("admin")
        courses = validated_data.pop("courses", [])

        semester = Semester.objects.create(admin=admin, **validated_data)
        semester.courses.set(courses)
        return semester

    def update(self, instance, validated_data):
        courses = validated_data.pop("courses", serializers.empty)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if courses is not serializers.empty:
            instance.courses.set(courses)
        return instance


class SemesterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ["id", "name", "is_current", "courses", "academic_year"]


### academic serializer


class AcademicYearListSerializer(serializers.ModelSerializer):
    program = ProgramListSerializer()

    class Meta:
        model = AcademicYear
        fields = ["id", "year", "is_current", "program"]


class AcademicYearWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ["id", "year", "is_current", "program"]

    def validate(self, data):
        """Валидация уникальности года в программе"""
        program = data.get("program") or (
            self.instance.program if self.instance else None
        )
        year = data.get("year") or (self.instance.year if self.instance else None)

        if program and year:
            queryset = AcademicYear.objects.filter(program=program, year=year)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"year": f"Для этой программы уже существует учебный год {year}"}
                )

        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


### module serializers


class ModuleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["name", "semester"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ["id", "name"]


class ModuleListSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ["id", "name", "is_current", "semester"]


### course  serializers


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name", "description"]


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["name", "description"]

    def update(self, instance, validated_data):
        """
        Автоматически устанавливаем не трогая админ
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


User = get_user_model()


class CourseAllocationListSerializer(serializers.ModelSerializer):
    lecturer = serializers.StringRelatedField()
    lecturer_id = serializers.PrimaryKeyRelatedField(source="lecturer", read_only=True)
    group = serializers.StringRelatedField()
    group_id = serializers.PrimaryKeyRelatedField(source="group", read_only=True)
    courses = CourseListSerializer(many=True, read_only=True)
    semester = serializers.StringRelatedField()
    semester_id = serializers.PrimaryKeyRelatedField(source="semester", read_only=True)

    class Meta:
        model = CourseAllocation
        fields = [
            "id",
            "lecturer",
            "lecturer_id",
            "courses",
            "semester",
            "semester_id",
            "group",
            "group_id",
        ]


class CourseAllocationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAllocation
        fields = ["lecturer", "courses", "semester", "group"]

    def create(self, validated_data):
        """Создание с ManyToMany courses"""
        courses = validated_data.pop("courses", [])
        allocation = CourseAllocation.objects.create(**validated_data)
        allocation.courses.set(courses)
        return allocation

    def update(self, instance, validated_data):
        """patch, put update с ManyToMany courses"""
        courses = validated_data.pop("courses", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if courses is not None:
            instance.courses.set(courses)
        return instance


class StudentCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAllocation
        fields = ["id", "lecturer", "courses", "semester", "group"]
