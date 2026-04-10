from rest_framework import serializers
from django.db.models import Sum
from .models import Invoice, Payment


class InvoiceListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(source="student", read_only=True)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "student_id",
            "student_name",
            "title",
            "amount",
            "status",
            "due_date",
            "total_paid",
            "created_at",
            "updated_at",
        ]


class InvoiceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["student", "title", "amount", "status", "due_date"]

    def create(self, validated_data):
        admin = self.context.get("admin")
        return Invoice.objects.create(admin=admin, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PaymentListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(source="student", read_only=True)
    invoice_title = serializers.CharField(source="invoice.title", read_only=True)
    invoice_id = serializers.PrimaryKeyRelatedField(source="invoice", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "student_id",
            "student_name",
            "invoice_id",
            "invoice_title",
            "amount",
            "payment_method",
            "comment",
            "created_at",
        ]


class PaymentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["invoice", "student", "amount", "payment_method", "comment"]

    def create(self, validated_data):
        admin = self.context.get("admin")
        payment = Payment.objects.create(admin=admin, **validated_data)
        payment.invoice.update_status()
        return payment


class StudentBalanceSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    total_charged = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
