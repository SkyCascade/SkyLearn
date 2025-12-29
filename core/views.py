from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from .models import AcademicYear, Semester, Program, Module, CourseAllocation, Course
from .serializers import (
    ModuleWriteSerializer,
    ModuleListSerializer,
    AcademicYearWriteSerializer,
    ProgramListSerializer,
    ProgramWriteSerializer,
    SemesterWriteSerializer,
    SemesterDetailSerializer,
    SemesterListSerializer,
    AcademicYearListSerializer,
    CourseListSerializer, 
    CourseWriteSerializer,
    CourseAllocationListSerializer, 
    CourseAllocationWriteSerializer
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
        context = super().get_serializer_context()
        if self.request.user.is_superuser:
            context["admin"] = self.request.user
        else:
            raise PermissionDenied("only admins can access this view")
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


### course views

class CourseListAPIView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Course.objects.filter(admin=user).order_by("name")
        else:
            raise PermissionDenied("Only superusers can access this view.")
    
class CourseCreateAPIView(generics.CreateAPIView):
    serializer_class = CourseWriteSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["admin"] = self.request.user
        return context
    
    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

class CourseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseWriteSerializer
        return CourseListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["admin"] = self.request.user
        return context
    

### course allocation views

class CourseAllocationListAPIView(generics.ListAPIView):
    serializer_class = CourseAllocationListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
            return CourseAllocation.objects.filter(admin=self.request.user)


class CourseAllocationCreateAPIView(generics.CreateAPIView):
    serializer_class = CourseAllocationWriteSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["admin"] = self.request.user
        return context
    
    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

class CourseAllocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = CourseAllocation.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseAllocationWriteSerializer
        return CourseAllocationListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["admin"] = self.request.user
        return context
    

class TeacherCourseAllocations(generics.ListAPIView):
    serializer_class = CourseAllocationListSerializer
    permission_classes = [IsLecturer]

    def get_queryset(self):
        user = self.request.user
        return CourseAllocation.objects.filter(lecturer=user)
        raise PermissionDenied("Only lecturers can access this view.")
