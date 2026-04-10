from django.contrib import admin
from .models import Invoice, Payment


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["title", "student", "amount", "status", "due_date", "created_at"]
    list_filter = ["status", "due_date"]
    search_fields = ["title", "student__student__first_name", "student__student__last_name"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["student", "invoice", "amount", "payment_method", "created_at"]
    list_filter = ["payment_method", "created_at"]
    search_fields = ["student__student__first_name", "student__student__last_name"]
