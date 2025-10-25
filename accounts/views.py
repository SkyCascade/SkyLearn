from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView
from django_filters.views import FilterView
from xhtml2pdf import pisa
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.db.models import Q
from accounts.filters import LecturerFilter, StudentFilter
from core.models import Semester, Session
from course.models import Course
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.viewsets import ModelViewSet
from core.permissions import IsAdminOrLecturer



from .models import Group ,Parent, Student, User ,Program
from .serializers import UserSerializer, StaffAddSerializer, StudentAddSerializer, StaffListSerializer, UserSerializer, UserUpdateSerializer ,GroupSerializer, StudentListSerializer, StudentDetailSerializer, StudentUpdateSerializer


User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Добавляем кастомные поля в токен
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Добавляем информацию о пользователе в ответ
        data['user'] = UserSerializer(self.user).data
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

User = get_user_model()



class LecturerListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра списка преподавателей
    """
    queryset = User.objects.filter(is_lecturer=True)
    serializer_class = StaffListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    View для получения и обновления данных пользователя
    Поддерживает GET (просмотр) и PUT/PATCH (обновление)
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Возвращает разные сериализаторы для разных действий
        """
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer
    
    def get_queryset(self):
        """
        Можно добавить дополнительную фильтрацию если нужно
        Например, только учителя или определенные роли
        """
        return User.objects.all()
    
    def update(self, request, *args, **kwargs):
        """
        Переопределяем для кастомного ответа или логики
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    

class UserDetailAPIView(APIView):
    """
    Retrieve user by ID
    """
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StaffCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        # Получаем всех пользователей с is_lecturer=True
        lecturers = User.objects.filter(is_lecturer=True)
        
        # Поддержка поиска (опционально)
        search_query = request.query_params.get('search', None)
        if search_query:
            lecturers = lecturers.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        serializer = StaffListSerializer(lecturers, many=True)
        return Response({
            'count': lecturers.count(),
            'lecturers': serializer.data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=StaffAddSerializer,
        responses={201: StaffAddSerializer}
    )
    def post(self, request):
        serializer = StaffAddSerializer(data=request.data)
        if serializer.is_valid():
            try:
                staff_user = serializer.save()
                return Response({
                    'message': 'Staff member created successfully',
                    'user_id': staff_user.id,
                    'username': staff_user.username
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StudentDeleteView(generics.DestroyAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = StudentAddSerializer


class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = StudentUpdateSerializer

class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = StudentListSerializer
    

class StudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsAdminOrLecturer]
    serializer_class = StudentDetailSerializer

# views.py - обновите StudentCreateView
class StudentCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Получить список программ и групп для фронтенда"""
        programs = Program.objects.all()
        groups = Group.objects.all()
        
        program_choices = [{'id': program.id, 'title': program.title} for program in programs]
        group_choices = [{'id': group.id, 'name': group.name} for group in groups]
        
        return Response({
            'programs': program_choices,
            'groups': group_choices,
            'levels': [
                {'value': value, 'label': label} for value, label in StudentAddSerializer.LEVEL
            ]
        })
    
    def post(self, request):
        serializer = StudentAddSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    student_instance = serializer.save()
                    
                    if not hasattr(student_instance, 'student'):
                        raise Exception("Student record was not created properly")
                
                # Получаем связанного пользователя
                user = student_instance.student
                
                response_data = {
                    'message': 'Student created successfully',
                    'data': {
                        'user_id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': f"{user.first_name} {user.last_name}",
                        'student_id': student_instance.id,
                        'level': student_instance.level,
                        'program': student_instance.program.title,
                    }
                }
                
                # Добавляем информацию о группе в ответ
                if student_instance.group:
                    response_data['data']['group'] = student_instance.group.name
                    response_data['data']['group_id'] = student_instance.group.id
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                print(f"Error creating student: {str(e)}")
                return Response({
                    'error': 'Failed to create student. Please try again.',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Validation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


# views.py в accounts app
class StudentsByGroupView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrLecturer]

    def get(self, request, group_name):
        group = get_object_or_404(Group, name=group_name)
        students = Student.objects.filter(group=group)
        serializer = StudentListSerializer(students, many=True)
        return Response({
            'group': group.name,
            'students': serializer.data
        }, status=status.HTTP_200_OK)