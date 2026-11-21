from django.contrib import admin
from .models import Request, Report

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'requester', 'status', 'rating', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('listing__title', 'requester__email', 'requester__full_name')
    ordering = ('-created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'reporter', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('listing__title', 'reporter__email', 'reason')
    list_editable = ('status',)
    ordering = ('-created_at',)
