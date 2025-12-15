from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Parent

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "get_full_name",
        "username",
        "email",
        "is_active",
        "is_student",
        "is_lecturer",
        "is_dep_head",
        "is_parent",
        "is_staff",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_lecturer",
        "is_parent",
        "is_staff",
    )

    # Edit form fields
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "gender", "phone", "address", "picture", "program", "department")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_student", "is_lecturer", "is_parent", "is_dep_head")}),
    )

    # Add form fields (important!)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "password1",
                "password2",
                "first_name",
                "last_name",
                "gender",
                "phone",
                "address",
                "picture",
                "program",
                "department",
                "is_staff",
                "is_active",
                "is_student",
                "is_lecturer",
                "is_parent",
                "is_dep_head",  # ✅ now visible on Add form
            ),
        }),
    )

admin.site.register(Student)
admin.site.register(Parent)

