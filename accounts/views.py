from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from attendance.permissions import IsLecturer
from config import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from rest_framework import status



from .models import Lecturer, Student, User, Group, Parent
from .serializers import (
    LecturerListSerializer,
    LecturerWriteSerializer,
    LecturerUpdateSerializer,

    StudentListSerializer, 
    StudentWriteSerializer,
    StudentUpdateSerializer,
    StudentListByGroupSerializer,

    GroupListSerializer,
    GroupWriteSerializer,

    ParentListSerializer,
    ParentWriteSerializer,
    ParentUpdateSerializer,
    UserSerializer
)



# ============================================================================
# LECTURER VIEWS
# ============================================================================

class LecturerCreateView(generics.CreateAPIView):
    serializer_class = LecturerWriteSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['admin'] = self.request.user
        return context

class LecturerListAPIView(generics.ListAPIView):
    serializer_class = LecturerListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Lecturer.objects.filter(admin=self.request.user)

class LecturerRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    serializer_class = LecturerListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Lecturer.objects.filter(admin=self.request.user)

class LecturerUpdateView(generics.UpdateAPIView):
    serializer_class = LecturerUpdateSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Lecturer.objects.filter(admin=self.request.user)

# ============================================================================
# STUDENT VIEWS
# ============================================================================  

class StudentListGroupAPIView(generics.ListAPIView):
    serializer_class = StudentListByGroupSerializer
    permission_classes = [IsLecturer]

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        return Student.objects.filter(group_id=group_id)

class StudentCreateView(generics.CreateAPIView):
    serializer_class = StudentWriteSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['admin'] = self.request.user
        return context

class StudentListAPIView(generics.ListAPIView):
    serializer_class = StudentListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Student.objects.filter(admin=self.request.user)

class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Student.objects.filter(admin=self.request.user)
    
class StudentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = StudentUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Разрешаем обновлять только своих студентов или все в зависимости от прав
        if self.request.user.is_superuser or self.request.user.is_dep_head:
            return Student.objects.all()
        # Для преподавателей - только студентов их групп
        elif self.request.user.is_lecturer:
            return Student.objects.filter(group__in=self.request.user.lecturer_groups.all())
        else:
            return Student.objects.none()
# ============================================================================
# GROUP VIEWS
# ============================================================================

class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupWriteSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
    
class GroupListAPIView(generics.ListAPIView):
    serializer_class = GroupListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Group.objects.filter(admin=self.request.user)

class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupWriteSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Group.objects.filter(admin=self.request.user)


# ============================================================================
# PARENT VIEWS
# ============================================================================  


class ParentCreateView(generics.CreateAPIView):
    serializer_class = ParentWriteSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['admin'] = self.request.user
        return context

    def perform_create(self, serializer):
        serializer.save()


class ParentListAPIView(generics.ListAPIView):
    serializer_class = ParentListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Parent.objects.filter(admin=self.request.user)
    

class ParentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ParentWriteSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Parent.objects.filter(admin=self.request.user)
    

class ParentUpdateView(generics.UpdateAPIView):
    serializer_class = ParentUpdateSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        user = self.request.user

        return Parent.objects.all(admin=user)
        
        
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


# ============================================================================
# Token views
# ============================================================================


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
    
    def post(self, request, *args, **kwargs):
        """
        Secure login that sets tokens in httpOnly cookies
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get tokens
        access_token = serializer.validated_data.get('access')
        refresh_token = serializer.validated_data.get('refresh')
        user_data = serializer.validated_data.get('user')
        
        # Create response
        response = Response({
            'user': user_data,
            'access': access_token,
            'refresh': refresh_token,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
        
        # Set httpOnly cookies
        # Access token (short-lived)
        response.set_cookie(
            key=settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token'),
            value=access_token,
            max_age=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds(),
            httponly=True,
            secure=not settings.DEBUG,  # True in production (HTTPS)
            samesite='Lax',  # Protection against CSRF
            domain=settings.SIMPLE_JWT.get('AUTH_COOKIE_DOMAIN'),
            path='/'
        )
        
        # Refresh token (long-lived)
        response.set_cookie(
            key=settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token'),
            value=refresh_token,
            max_age=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').total_seconds(),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            domain=settings.SIMPLE_JWT.get('AUTH_COOKIE_DOMAIN'),
            path='/'
        )
        
        return response


class SecureTokenRefreshView(TokenRefreshView):
    """
    Secure token refresh that uses httpOnly cookies
    """
    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token')
        )
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            # Validate and refresh
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            # If rotation is enabled, get new refresh token
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                refresh.set_jti()
                refresh.set_exp()
                new_refresh_token = str(refresh)
            else:
                new_refresh_token = refresh_token
            
            response = Response({
                'message': 'Token refreshed successfully',
                'access': access_token,
                'refresh': new_refresh_token if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False) else new_refresh_token
            }, status=status.HTTP_200_OK)
            
            # Set new access token cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token'),
                value=access_token,
                max_age=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds(),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                domain=settings.SIMPLE_JWT.get('AUTH_COOKIE_DOMAIN'),
                path='/'
            )
            
            # Set new refresh token cookie if rotation is enabled
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                response.set_cookie(
                    key=settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token'),
                    value=new_refresh_token,
                    max_age=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').total_seconds(),
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax',
                    domain=settings.SIMPLE_JWT.get('AUTH_COOKIE_DOMAIN'),
                    path='/'
                )
            
            return response
            
        except (TokenError, InvalidToken) as e:
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserProfileView(APIView):
    """
    Возвращает профиль текущего пользователя
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        data = serializer.data
        
        # Если это студент, добавляем данные студента
        if request.user.is_student and hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            student_serializer = StudentListSerializer(student)
            data['student_data'] = student_serializer.data
            
        return Response(data)