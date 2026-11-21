from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'hostel', 'phone', 'role', 'is_email_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_email_verified', 'is_active', 'date_joined')
    search_fields = ('email', 'full_name', 'phone', 'hostel')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'phone', 'hostel', 'avatar')}),
        (_('ReFind Permissions'), {'fields': ('role', 'is_email_verified', 'is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password', 'role', 'is_email_verified'),
        }),
    )
