from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'sender', 'recipient', 'body_preview', 'sent_at', 'is_read')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__email', 'recipient__email', 'body', 'listing__title')
    ordering = ('-sent_at',)

    def body_preview(self, obj):
        return obj.body[:40] + ('...' if len(obj.body) > 40 else '')
    body_preview.short_description = 'Message Body'
