from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from course.models import Program
from .models import User, Student, Parent, RELATION_SHIP, LEVEL, GENDERS, Group
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()




class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'is_student',
            'is_lecturer',
            'is_parent',
            'is_dep_head',
            'is_superuser',
            'is_active',
            'gender',
            'phone',
            'address',
            'picture_url',
            'date_joined',
            'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name
    
    def get_role(self, obj):
        return obj.get_user_role
    
    def get_picture_url(self, obj):
        return obj.get_picture()





class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'first_name', 
            'last_name',
            'gender',
            'address', 
            'phone',
            'email'
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        """
        Проверяем, что email уникален, исключая текущего пользователя
        """
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        """
        Обновление данных пользователя
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StaffAddSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'gender', 'address',
            'phone', 'email'
        ]
    

    @transaction.atomic
    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            gender=validated_data.get('gender'),
            address=validated_data.get('address'),
            phone=validated_data.get('phone'),
            is_lecturer=True
        )
        return user

class StaffListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'gender', 'address', 'phone', 'email', 'user_role',
            'date_joined', 'last_login'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name
    
    def get_user_role(self, obj):
        return obj.get_user_role
    

class StudentListSerializer(serializers.ModelSerializer):
    # Поля из User модели (обращаемся напрямую через student)
    username = serializers.CharField(source='student.username')
    first_name = serializers.CharField(source='student.first_name')
    last_name = serializers.CharField(source='student.last_name')
    full_name = serializers.SerializerMethodField()
    gender = serializers.CharField(source='student.gender')
    address = serializers.CharField(source='student.address')
    phone = serializers.CharField(source='student.phone')
    email = serializers.EmailField(source='student.email')
    user_role = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(source='student.date_joined')
    last_login = serializers.DateTimeField(source='student.last_login')
    
    # Поля из Student модели
    group = serializers.StringRelatedField()
    program_name = serializers.CharField(source='program.title', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'gender', 'address', 'phone', 'email', 'user_role',
            'date_joined', 'last_login', 'group', 'level', 'program', 'program_name'
        ]
    
    def get_full_name(self, obj):
        # Теперь obj - это Student объект, поэтому обращаемся к student
        return obj.student.get_full_name if obj.student else ""
    
    def get_user_role(self, obj):
        # Теперь obj - это Student объект, поэтому обращаемся к student
        return obj.student.get_user_role if obj.student else _("Student")
    
class StudentAddSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    gender = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    user_role = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.DateTimeField(source='student.date_joined', read_only=True)
    last_login = serializers.DateTimeField(source='student.last_login', read_only=True)
    
    level = serializers.ChoiceField(choices=LEVEL)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all())
    group = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'username', 'first_name', 'last_name', 'full_name', 'gender', 'address',
            'phone', 'email', 'user_role', 'level', 'program', 'group', 
            'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login', 'full_name', 'user_role', 'group']

    def get_full_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_user_role(self, obj):
        return "student"

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError("Email has been taken, try another email address.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value, is_active=True).exists():
            raise serializers.ValidationError("Username has been taken, try another username.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        # Извлекаем данные для пользователя
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        gender = validated_data.pop('gender')
        address = validated_data.pop('address')
        phone = validated_data.pop('phone')
        
        level = validated_data.pop('level')
        program = validated_data.pop('program')
        
        # Создаем пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            address=address,
            phone=phone,
            is_student=True
        )
        
        # Создаем студента
        student = Student.objects.create(
            student=user,
            level=level,
            program=program
        )
        
        return student

    def to_representation(self, instance):
        # Переопределяем представление для чтения
        representation = super().to_representation(instance)
        # Добавляем данные пользователя для ответа
        representation['username'] = instance.student.username
        representation['first_name'] = instance.student.first_name
        representation['last_name'] = instance.student.last_name
        representation['email'] = instance.student.email
        representation['gender'] = instance.student.gender
        representation['address'] = instance.student.address
        representation['phone'] = instance.student.phone
        return representation





class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'gender', 'email', 
            'phone', 'address', 'picture'
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProgramUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['program']


class ParentAddSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        max_length=30,
        write_only=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        max_length=30,
        write_only=True,
        style={'input_type': 'password'}
    )
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    relation_ship = serializers.ChoiceField(choices=RELATION_SHIP)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'address',
            'phone', 'email', 'student', 'relation_ship', 
            'password1', 'password2'
        ]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError("Email has been taken, try another email address.")
        return value

    def validate(self, attrs):
        if attrs.get('password1') != attrs.get('password2'):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password1 = validated_data.pop('password1')
        password2 = validated_data.pop('password2')
        student = validated_data.pop('student')
        relation_ship = validated_data.pop('relation_ship')
        
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=password1,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            address=validated_data.get('address'),
            phone=validated_data.get('phone'),
            is_parent=True
        )
        
        Parent.objects.create(
            user=user,
            student=student,
            relation_ship=relation_ship
        )
        
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError(
                "There is no user registered with the specified E-mail address."
            )
        return value


class StudentDetailSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    program_name = serializers.CharField(source='program.title', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student', 'level', 'program', 'program_name']


class ParentDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    student_info = StudentDetailSerializer(source='student', read_only=True)

    class Meta:
        model = Parent
        fields = ['id', 'user', 'student', 'student_info', 'relation_ship']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']