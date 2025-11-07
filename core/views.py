from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts.decorators import admin_required, lecturer_required
from accounts.models import User, Student


from .models import NewsAndEvents, ActivityLog, Session, Semester
from accounts.models import Student, User


# ########################################################
# News & Events
# ########################################################




from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .models import NewsAndEvents, Session, Semester, ActivityLog
from .serializers import (
    NewsAndEventsSerializer, 
    NewsAndEventsDetailSerializer,
    SessionSerializer,
    SessionDetailSerializer,
    SemesterSerializer,
    SemesterDetailSerializer,
    DashboardSerializer,
    HomeSerializer
)
from .permissions import IsLecturer, IsAdminOrLecturer

User = get_user_model()

# News and Events Views
class NewsAndEventsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = NewsAndEvents.objects.all().order_by("-updated_date")
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return NewsAndEventsDetailSerializer
        return NewsAndEventsSerializer
    
    def get_permissions(self):
        # Для создания, обновления и удаления требуются права лектора или админа
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrLecturer()]
        # Для просмотра достаточно обычной аутентификации
        return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        """Get all news and events (ordered by updated_date)"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "title": "News & Events",
            "items": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Create new post"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                "message": f"{instance.title} has been uploaded.",
                "data": NewsAndEventsDetailSerializer(instance).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Please correct the error(s) below.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update post"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            updated_instance = serializer.save()
            return Response({
                "message": f"{updated_instance.title} has been updated.",
                "data": NewsAndEventsDetailSerializer(updated_instance).data
            })
        return Response({
            "message": "Please correct the error(s) below.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete post"""
        instance = self.get_object()
        post_title = instance.title
        instance.delete()
        return Response({
            "message": f"{post_title} has been deleted."
        }, status=status.HTTP_204_NO_CONTENT)


# Session Views
class SessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Session.objects.all().order_by("-is_current_session", "-session")
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return SessionDetailSerializer
        return SessionSerializer
    
    def list(self, request, *args, **kwargs):
        """Get list of all sessions"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"sessions": serializer.data})
    
    def create(self, request, *args, **kwargs):
        """Add new session"""
        print("Received data:", request.data)
        serializer = SessionSerializer(data=request.data)
        
        if serializer.is_valid():
            print("Data is valid")
            
            # Если создается новая текущая сессия, снимаем текущий статус со старой
            if serializer.validated_data.get('is_current_session'):
                self.unset_current_session()
            
            instance = serializer.save()
            return Response({
                "message": "Session added successfully.",
                "data": SessionDetailSerializer(instance).data
            }, status=status.HTTP_201_CREATED)
        else:
            print("Validation errors:", serializer.errors)
            return Response({
                "message": "Please correct the error(s) below.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update session"""
        instance = self.get_object()
        serializer = SessionSerializer(instance, data=request.data, partial=kwargs.get('partial', False))
        
        if serializer.is_valid():
            # Если эта сессия становится текущей, снимаем текущий статус с других
            if serializer.validated_data.get('is_current_session'):
                self.unset_current_session()
            
            updated_instance = serializer.save()
            return Response({
                "message": "Session updated successfully.",
                "data": SessionDetailSerializer(updated_instance).data
            })
        else:
            return Response({
                "message": "Please correct the error(s) below.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete session"""
        instance = self.get_object()
        if instance.is_current_session:
            return Response({
                "error": "You cannot delete the current session."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        session_name = instance.session
        instance.delete()
        return Response({
            "message": f"Session {session_name} successfully deleted."
        }, status=status.HTTP_204_NO_CONTENT)
    
    def unset_current_session(self):
        """Unset current session from all other sessions"""
        current_sessions = Session.objects.filter(is_current_session=True)
        for session in current_sessions:
            session.is_current_session = False
            session.save()
        print(f"Unset current session from {current_sessions.count()} sessions")




# Semester Views
# Semester Views
# Semester Views
class SemesterViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Semester.objects.all().order_by("-is_current_semester", "-semester")
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return SemesterDetailSerializer
        return SemesterSerializer
    
    def get_permissions(self):
        # Для создания, обновления и удаления требуются права администратора
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        # Для просмотра (list, retrieve) достаточно обычной аутентификации
        return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        """Get list of all semesters"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"semesters": serializer.data})
    
    def create(self, request, *args, **kwargs):
        """Add new semester (admin only)"""
        print("=== SEMESTER CREATE DEBUG ===")
        print("Request data:", request.data)
        
        serializer = SemesterSerializer(data=request.data)
        if serializer.is_valid():
            print("Data is valid")
            # Unset current semester if new one is being set as current
            if serializer.validated_data.get('is_current_semester'):
                self.unset_current_semester()
            
            instance = serializer.save()
            return Response({
                "message": "Semester added successfully.",
                "data": SemesterDetailSerializer(instance).data
            }, status=status.HTTP_201_CREATED)
        else:
            print("Validation errors:", serializer.errors)
            return Response({
                "message": "Please correct the error(s) below.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update semester (admin only)"""
        instance = self.get_object()
        serializer = SemesterSerializer(instance, data=request.data, partial=kwargs.get('partial', False))
        if serializer.is_valid():
            # Unset current semester if this one is being set as current
            if serializer.validated_data.get('is_current_semester'):
                self.unset_current_semester()
            
            updated_instance = serializer.save()
            return Response({
                "message": "Semester updated successfully!",
                "data": SemesterDetailSerializer(updated_instance).data
            })
        return Response({
            "message": "Please correct the error(s) below.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete semester (admin only)"""
        instance = self.get_object()
        if instance.is_current_semester:
            return Response({
                "error": "You cannot delete the current semester."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.delete()
        return Response({
            "message": "Semester successfully deleted."
        }, status=status.HTTP_204_NO_CONTENT)
    
    def unset_current_semester(self):
        """Unset current semester"""
        current_semester = Semester.objects.filter(is_current_semester=True).first()
        if current_semester:
            current_semester.is_current_semester = False
            current_semester.save()


