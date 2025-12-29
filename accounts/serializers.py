from rest_framework import serializers
from .models import Parent, Student, Lecturer, Group, User
from core.models import Program
from .utils import generate_password, send_new_account_email



# ============================================================================
# BASE SERIALIZERS
# ============================================================================


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "address", "gender", "date_joined", "is_lecturer", "is_student", "is_superuser", "is_parent", "is_staff"]


# ============================================================================
# Lecturer SERIALIZERS
# ============================================================================


class LecturerListSerializer(serializers.ModelSerializer):
    lecturer = UserSerializer()
    lecturer_id = serializers.PrimaryKeyRelatedField(source='lecturer', read_only=True)

    class Meta:
        model = Lecturer
        fields = ["id", "lecturer", "lecturer_id"]

class LecturerWriteSerializer(serializers.ModelSerializer):
    lecturer = serializers.DictField(write_only=True)

    class Meta:
        model = Lecturer
        fields = ["lecturer"]

    def create(self, validated_data):
        """
        Создаем нового лектора с генерацией пароля и отправкой email
        """
        lecturer_data = validated_data.pop("lecturer", {})
        # Генерируем username если не предоставлен
        email = lecturer_data.get("email", "")
        if not lecturer_data.get("username"):
            lecturer_data["username"] = email.split("@")[0] + "_" + str(int(__import__('time').time() * 1000))
        
        # Генерируем пароль
        password = generate_password()
        
        # Создаем пользователя
        user = User.objects.create_user(**lecturer_data, password=password)
        user.is_lecturer = True
        user.save()
        
        # Отправляем email с учетными данными
        if user.email:
            send_new_account_email(user, password)
        
        return Lecturer.objects.create(lecturer=user, admin=self.context['admin'])


class LecturerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "email", "address", "gender", "last_name"]

    def update(self, instance, validated_data):
        """
        Обновляем данные лектора
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
        model = Program
        fields = ["id", "name"]


class GroupSerializer(serializers.ModelSerializer):
    program = ProgramSerializer()

    class Meta:
        model = Group
        fields = ["id", "name", "program"]

class StudentListSerializer(serializers.ModelSerializer):
    student = UserSerializer()
    group = GroupSerializer()

    class Meta:
        model = Student
        fields = ["id", "student", "group"]



class StudentWriteSerializer(serializers.ModelSerializer):
    student = serializers.DictField(write_only=True)

    class Meta:
        model = Student
        fields = ["student", "group"]

    def create(self, validated_data):
        """
        Создаем нового студента с генерацией пароля и отправкой email
        """
        student_data = validated_data.pop("student", {})
        # Извлекаем email для использования в username если username не предоставлен
        email = student_data.get("email", "")
        if not student_data.get("username"):
            student_data["username"] = email.split("@")[0] + "_" + str(int(__import__('time').time() * 1000))
        
        # Генерируем пароль
        password = generate_password()
        
        # Создаем пользователя
        user = User.objects.create_user(**student_data, password=password)
        user.is_student = True
        user.save()
        
        # Отправляем email с учетными данными
        if user.email:
            send_new_account_email(user, password)
        
        return Student.objects.create(student=user, group=validated_data.get("group"), admin=self.context['admin'])

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'gender', 'phone', 'address', 'picture']


class StudentUpdateSerializer(serializers.ModelSerializer):
    student = UserUpdateSerializer()
    
    class Meta:
        model = Student
        fields = ['id', 'student', 'group']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('student', {})
        
        if user_data:
            user_serializer = UserUpdateSerializer(
                instance.student, 
                data=user_data, 
                partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
        return super().update(instance, validated_data)
    
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
        fields = ["id", "first_name", "last_name", "phone", "student", "user"]


class ParentWriteSerializer(serializers.ModelSerializer):
    user = serializers.DictField(write_only=True, required=False)
    
    class Meta:
        model = Parent
        fields = ["user", "student", "first_name", "last_name", "phone", "email"]
    
    def create(self, validated_data):
        """
        Создаем нового родителя с генерацией пароля и отправкой email
        """
        user_data = validated_data.pop("user", {})
        
        # Если данные пользователя не предоставлены, используем данные родителя
        if not user_data:
            user_data = {
                "first_name": validated_data.get("first_name", ""),
                "last_name": validated_data.get("last_name", ""),
                "email": validated_data.get("email", ""),
                "phone": validated_data.get("phone", ""),
            }
        
        # Генерируем username если не предоставлен
        email = user_data.get("email") or validated_data.get("email", "")
        if not user_data.get("username"):
            user_data["username"] = email.split("@")[0] + "_parent_" + str(int(__import__('time').time() * 1000))
        
        # Генерируем пароль
        password = generate_password()
        
        # Создаем пользователя
        user = User.objects.create_user(**user_data, password=password)
        user.is_parent = True
        user.save()
        
        # Отправляем email с учетными данными
        if user.email:
            send_new_account_email(user, password)
        
        return Parent.objects.create(
            user=user, 
            student=validated_data.get("student"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
            email=validated_data.get("email", ""),
            admin=self.context.get('admin')
        )
    
    def update(self, instance, validated_data):
        """
        Автоматически устанавливаем не трогая админ
        """
        validated_data.pop("user", None)  # Удаляем user из update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class UserForParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'gender', 'phone', 'address', 'picture']

class ParentUpdateSerializer(serializers.ModelSerializer):
    user = UserForParentSerializer()
    
    class Meta:
        model = Parent
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 
                 'relation_ship', 'user', 'student']
        read_only_fields = ['id', 'student']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Обновляем User
        if user_data:
            user_serializer = UserForParentSerializer(
                instance.user, 
                data=user_data, 
                partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        return super().update(instance, validated_data)

    

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