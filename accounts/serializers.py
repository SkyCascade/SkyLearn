from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from course.models import Program
from .models import User, Student, Parent, RELATION_SHIP, LEVEL, GENDERS
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 
            'phone', 'address', 'gender', 'picture', 'is_student', 
            'is_lecturer', 'is_parent', 
        ]
        read_only_fields = ['id']


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


class StudentAddSerializer(serializers.ModelSerializer):
    
    level = serializers.ChoiceField(choices=LEVEL)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all())

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'gender', 'address',
            'phone', 'email', 'level', 'program'
        ]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError("Email has been taken, try another email address.")
        return value

    @transaction.atomic
    def create(self, validated_data):
       
        level = validated_data.pop('level')
        program = validated_data.pop('program')
        
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            gender=validated_data.get('gender'),
            address=validated_data.get('address'),
            phone=validated_data.get('phone'),
            is_student=True
        )
        
        Student.objects.create(
            student=user,
            level=level,
            program=program
        )
        
        return user


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