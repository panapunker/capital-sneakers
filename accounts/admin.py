from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'rol', 'activo', 'fecha_creacion')
    list_filter = ('rol', 'activo', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-fecha_creacion',)

    fieldsets = UserAdmin.fieldsets + (
        ('Datos Capital Sneakers', {
            'fields': ('rol', 'telefono', 'foto', 'activo')
        }),
    )