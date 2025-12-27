from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from accounts.decorators import admin_required, lecturer_required
from accounts.models import User, Student
from rest_framework.exceptions import PermissionDenied



# ########################################################
# News & Events
# ########################################################




from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .models import AcademicYear, Semester, Program, Module
from .serializers import (
    ModuleWriteSerializer,
    ModuleListSerializer,
    AcademicYearWriteSerializer,
    ProgramListSerializer,
    ProgramWriteSerializer,
    SemesterWriteSerializer,
    SemesterDetailSerializer,
    SemesterListSerializer,
    AcademicYearListSerializer
)
from .permissions import IsLecturer, IsAdminOrLecturer

User = get_user_model()


### semester views

class SemesterListAPIView(generics.ListAPIView):
    serializer_class = SemesterListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Semester.objects.filter(admin=user).order_by("-is_current", "-name")
        else:
            raise PermissionDenied("Only superusers can access this view.")


class SemesterCreateAPIView(generics.CreateAPIView):
    serializer_class = SemesterWriteSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        """giving admin to serializer context"""
        if self.request.user.is_superuser:
            admin = self.request.user
        else:
            raise PermissionDenied("only admins can access this view")
        context = super().get_serializer_context()
        context["admin"] = admin
        return context

class SemesterUpdateAPIView(generics.UpdateAPIView):
    serializer_class = SemesterWriteSerializer
    permission_classes = [IsAdminUser]
    queryset = Semester.objects.all()

    def get_serializer_context(self):
        """giving admin to serializer context"""
        if self.request.user.is_superuser:
            admin = self.request.user
        else:
            raise PermissionDenied("only admins can access this view")
        context = super().get_serializer_context()
        context["admin"] = admin
        return context

class SemesterRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = SemesterDetailSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Semester.objects.filter(admin=self.request.user)
        raise PermissionDenied("Only admins can access this view.")

    
### program views

class ProgramCreateAPIView(generics.CreateAPIView):
    serializer_class = ProgramWriteSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)


class ProgramUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ProgramWriteSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Program.objects.filter(admin=self.request.user)
        raise PermissionDenied("Only admins can access this view.")

class ProgramRetrieveDestroyAPIView(generics.DestroyAPIView):
    serializer_class = ProgramWriteSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Program.objects.filter(admin=self.request.user)
        raise PermissionDenied("Only admins can access this view.")
    

class ProgramListAPIView(generics.ListAPIView):
    serializer_class = ProgramListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Program.objects.filter(admin=self.request.user)
        raise PermissionDenied("Only admins can access this view.")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language"] = self.request.query_params.get("lang", "ru")
        return context


### academic year views

class AcademicYearCreateAPIView(generics.CreateAPIView):
    serializer_class = AcademicYearWriteSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)


class AcademicYearUpdateAPIView(generics.UpdateAPIView):
    serializer_class = AcademicYearWriteSerializer
    permission_classes = [IsAdminUser]
    queryset = AcademicYear.objects.all()

class AcademicYearRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = AcademicYearWriteSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return AcademicYear.objects.filter(admin=self.request.user)
        raise PermissionDenied("Only admins can access this view.")

class AcademicYearListAPIView(generics.ListAPIView):
    serializer_class = AcademicYearListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return AcademicYear.objects.filter(admin=self.request.user)
        raise PermissionDenied("Only admins can access this view.")

### module views

class ModuleCreateAPIView(generics.CreateAPIView):
    serializer_class = ModuleWriteSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

class ModuleUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ModuleWriteSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Module.objects.filter(admin=self.request.user)

class ModuleListAPIView(generics.ListAPIView):
    serializer_class = ModuleListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Module.objects.filter(admin=self.request.user)
        raise PermissionDenied("Only admins can access this view.")

class ModuleRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = ModuleListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Module.objects.filter(admin=self.request.user)
        raise PermissionDenied("Only admins can access this view.")
