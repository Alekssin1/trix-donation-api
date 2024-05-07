from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "admin", "last_login")
    list_filter = ("admin",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": ("name",
                           "surname",
                           "avatar",
                           "blocked",
                           "declined_request_counter",
                           )
            },
        ),
        ("Login info", {"fields": ("last_login",)}),
        (
            "Permissions",
            {
                "fields": (
                    "admin",
                    "is_staff",
                    "is_active",
                )
            },
        ),
    )
    readonly_fields = ("last_login",)
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": (
            "email", "password1", "password2")}),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)