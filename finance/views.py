from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.db.models import Sum

from accounts.models import Student
from .models import Invoice, Payment
from .serializers import (
    InvoiceListSerializer,
    InvoiceWriteSerializer,
    PaymentListSerializer,
    PaymentWriteSerializer,
    StudentBalanceSerializer,
)
from .permissions import IsStudentOwner


# ===================== Admin: Invoices =====================


class InvoiceListAPIView(generics.ListAPIView):
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")
        qs = Invoice.objects.filter(admin=self.request.user)
        student_id = self.request.query_params.get("student")
        status = self.request.query_params.get("status")
        if student_id:
            qs = qs.filter(student_id=student_id)
        if status:
            qs = qs.filter(status=status)
        return qs


class InvoiceCreateAPIView(generics.CreateAPIView):
    serializer_class = InvoiceWriteSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")
        context["admin"] = self.request.user
        return context


class InvoiceRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")
        return Invoice.objects.filter(admin=self.request.user)


class InvoiceUpdateAPIView(generics.UpdateAPIView):
    serializer_class = InvoiceWriteSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")
        return Invoice.objects.filter(admin=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["admin"] = self.request.user
        return context


class InvoiceDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")
        return Invoice.objects.filter(admin=self.request.user)


# ===================== Admin: Payments =====================


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")
        qs = Payment.objects.filter(admin=self.request.user)
        student_id = self.request.query_params.get("student")
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentWriteSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")
        context["admin"] = self.request.user
        return context


class PaymentDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")
        return Payment.objects.filter(admin=self.request.user)

    def perform_destroy(self, instance):
        invoice = instance.invoice
        instance.delete()
        invoice.update_status()


# ===================== Admin: Student Balance =====================


class StudentBalanceAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("Only admins can access this view.")

        try:
            student = Student.objects.get(pk=pk, admin=request.user)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

        total_charged = (
            Invoice.objects.filter(student=student, admin=request.user).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )
        total_paid = (
            Payment.objects.filter(student=student, admin=request.user).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        data = {
            "student_id": student.pk,
            "student_name": student.get_full_name(),
            "total_charged": total_charged,
            "total_paid": total_paid,
            "balance": total_charged - total_paid,
        }
        serializer = StudentBalanceSerializer(data)
        return Response(serializer.data)


# ===================== Student: My Finance =====================


class MyInvoicesAPIView(generics.ListAPIView):
    serializer_class = InvoiceListSerializer
    permission_classes = [IsStudentOwner]

    def get_queryset(self):
        student = self.request.user.student_profile
        return Invoice.objects.filter(student=student)


class MyPaymentsAPIView(generics.ListAPIView):
    serializer_class = PaymentListSerializer
    permission_classes = [IsStudentOwner]

    def get_queryset(self):
        student = self.request.user.student_profile
        return Payment.objects.filter(student=student)


class MyBalanceAPIView(APIView):
    permission_classes = [IsStudentOwner]

    def get(self, request):
        student = request.user.student_profile

        total_charged = (
            Invoice.objects.filter(student=student).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        total_paid = (
            Payment.objects.filter(student=student).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        data = {
            "student_id": student.pk,
            "student_name": student.get_full_name(),
            "total_charged": total_charged,
            "total_paid": total_paid,
            "balance": total_charged - total_paid,
        }
        serializer = StudentBalanceSerializer(data)
        return Response(serializer.data)
