from rest_framework import serializers
from .models import Parent, Student, Lecturer, Group, User



# ============================================================================
# BASE SERIALIZERS
# ============================================================================


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


# ============================================================================
# Lecturer SERIALIZERS
# ============================================================================


class LecturerListSerializer(serializers.ModelSerializer):
    lecturer = UserSerializer()

    class Meta:
        model = Lecturer
        fields = ["id"]

class LecturerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ["lecturer"]
    
    def update(self, instance, validated_data):
        """
        Автоматически устанавливаем не трогая админ
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ============================================================================
# Student SERIALIZERS
# ============================================================================

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = 'core.Program'
        fields = ["id", "name"]


class GroupSerializer(serializers.ModelSerializer):
    program = ProgramSerializer()

    class Meta:
        model = Group
        fields = ["id", "name"]

class StudentListSerializer(serializers.ModelSerializer):
    student = UserSerializer()
    group = GroupSerializer()

    class Meta:
        model = Student
        fields = ["id", "group"]

class StudentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["student", "group"]
    
    def update(self, instance, validated_data):
        """
        Автоматически устанавливаем не трогая админ
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
# ============================================================================
# Parent SERIALIZERS
# ============================================================================

class UserForStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","first_name", "last_name", "email"]

class StudentSerializer(serializers.ModelSerializer):
    student = UserForStudentSerializer()
    class Meta:
        model = Student
        fields = ["id", "student", "group"]

class ParentListSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    student = StudentSerializer()

    class Meta:
        model = Parent
        fields = ["id", "first_name", "last_name", "phone", "student"]


class ParentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ["user", "student", "first_name", "last_name", "phone", "email"]
    
    def update(self, instance, validated_data):
        """
        Автоматически устанавливаем не трогая админ
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

# ============================================================================
# Group serializers
# ============================================================================

class GroupListSerializer(serializers.ModelSerializer):
    program = ProgramSerializer()

    class Meta:
        model = Group
        fields = ["id", "name", "program"]

class GroupWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name", "program"]
    
    def update(self, instance, validated_data):
        """
        Автоматически устанавливаем не трогая админ
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance