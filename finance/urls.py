from django.urls import path

from . import views

urlpatterns = [
    # Admin: Invoices
    path("invoices/", views.InvoiceListAPIView.as_view(), name="invoice-list"),
    path(
        "invoices/create/", views.InvoiceCreateAPIView.as_view(), name="invoice-create"
    ),
    path(
        "invoices/<int:pk>/",
        views.InvoiceRetrieveAPIView.as_view(),
        name="invoice-detail",
    ),
    path(
        "invoices/<int:pk>/update/",
        views.InvoiceUpdateAPIView.as_view(),
        name="invoice-update",
    ),
    path(
        "invoices/<int:pk>/delete/",
        views.InvoiceDeleteAPIView.as_view(),
        name="invoice-delete",
    ),
    # Admin: Payments
    path("payments/", views.PaymentListAPIView.as_view(), name="payment-list"),
    path(
        "payments/create/", views.PaymentCreateAPIView.as_view(), name="payment-create"
    ),
    path(
        "payments/<int:pk>/delete/",
        views.PaymentDeleteAPIView.as_view(),
        name="payment-delete",
    ),
    # Admin: Student Balance
    path(
        "students/<int:pk>/balance/",
        views.StudentBalanceAPIView.as_view(),
        name="student-balance",
    ),
    # Student: My Finance
    path("my/invoices/", views.MyInvoicesAPIView.as_view(), name="my-invoices"),
    path("my/payments/", views.MyPaymentsAPIView.as_view(), name="my-payments"),
    path("my/balance/", views.MyBalanceAPIView.as_view(), name="my-balance"),
]
