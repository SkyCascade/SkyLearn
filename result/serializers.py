from rest_framework import serializers
from .models import Grade_1st_module, Grade_2nd_module, Grade_semester

class StudentGradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        fields = ['student', 'student_name', 'student_id']

# Сериализаторы для студентов (только чтение)
class StudentGrade1stModuleSerializer(StudentGradeSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)

    class Meta(StudentGradeSerializer.Meta):
        model = Grade_1st_module
        fields = StudentGradeSerializer.Meta.fields + [
            'id', 'course', 'course_title', 'course_code', 'lecturer', 'lecturer_name',
            'attendance', 'activities', 'exam', 'total', 'grade'
        ]
        read_only_fields = ['attendance', 'activities', 'exam', 'total', 'grade']

class StudentGrade2ndModuleSerializer(StudentGradeSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)

    class Meta(StudentGradeSerializer.Meta):
        model = Grade_2nd_module
        fields = StudentGradeSerializer.Meta.fields + [
            'id', 'course', 'course_title', 'course_code', 'lecturer', 'lecturer_name',
            'attendance', 'activities', 'exam', 'total', 'grade'
        ]
        read_only_fields = ['attendance', 'activities', 'exam', 'total', 'grade']

class StudentGradeSemesterSerializer(StudentGradeSerializer):
    course_title = serializers.CharField(source='course.name', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)
    semester_name = serializers.CharField(source='semester.semester', read_only=True)

    class Meta(StudentGradeSerializer.Meta):
        model = Grade_semester
        fields = StudentGradeSerializer.Meta.fields + [
            'id', 'course', 'course_title', 'course_code', 'lecturer', 'lecturer_name',
            'semester', 'semester_name', 'attendance', 'activities', 'exam', 'total', 'grade'
        ]
        read_only_fields = ['attendance', 'activities', 'exam', 'total', 'grade']

# Сериализаторы для преподавателей (можно редактировать)
class LecturerGrade1stModuleSerializer(StudentGradeSerializer):
    course_title = serializers.CharField(source='course.name', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)

    class Meta(StudentGradeSerializer.Meta):
        model = Grade_1st_module
        fields = StudentGradeSerializer.Meta.fields + [
            'id', 'course', 'course_title', 'course_code', 'lecturer', 'lecturer_name',
            'attendance', 'activities', 'exam', 'total', 'grade'
        ]

    def validate(self, data):
        attendance = data.get('attendance', self.instance.attendance if self.instance else 0)
        activities = data.get('activities', self.instance.activities if self.instance else 0)
        exam = data.get('exam', self.instance.exam if self.instance else 0)
        
        data['total'] = attendance + activities + exam
        return data

class LecturerGrade2ndModuleSerializer(StudentGradeSerializer):
    course_title = serializers.CharField(source='course.name', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)

    class Meta(StudentGradeSerializer.Meta):
        model = Grade_2nd_module
        fields = StudentGradeSerializer.Meta.fields + [
            'id', 'course', 'course_title', 'course_code', 'lecturer', 'lecturer_name',
            'attendance', 'activities', 'exam', 'total', 'grade'
        ]

    def validate(self, data):
        attendance = data.get('attendance', self.instance.attendance if self.instance else 0)
        activities = data.get('activities', self.instance.activities if self.instance else 0)
        exam = data.get('exam', self.instance.exam if self.instance else 0)
        
        data['total'] = attendance + activities + exam
        return data

class LecturerGradeSemesterSerializer(StudentGradeSerializer):
    course_title = serializers.CharField(source='course.name', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)
    semester_name = serializers.CharField(source='semester.semester', read_only=True)

    class Meta(StudentGradeSerializer.Meta):
        model = Grade_semester
        fields = StudentGradeSerializer.Meta.fields + [
            'id', 'course', 'course_title', 'lecturer', 'lecturer_name',
            'semester', 'semester_name', 'attendance', 'activities', 'exam', 'total', 'grade'
        ]

    def validate(self, data):
        attendance = data.get('attendance', self.instance.attendance if self.instance else 0)
        activities = data.get('activities', self.instance.activities if self.instance else 0)
        exam = data.get('exam', self.instance.exam if self.instance else 0)
        
        data['total'] = attendance + activities + exam
        return data

# Сериализатор для массового обновления оценок (ОСТАВЛЯЕМ ТОЛЬКО ЭТОТ)
class BulkGradeUpdateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    attendance = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    activities = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    exam = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)

class BulkGradesUpdateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    grade_type = serializers.ChoiceField(choices=['1st_module', '2nd_module', 'semester'])
    grades = BulkGradeUpdateSerializer(many=True)

    def validate(self, data):
        # Дополнительная валидация если нужно
        return data