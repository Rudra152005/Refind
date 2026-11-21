from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'listing_type', 'price', 'condition', 'status', 'created_at')
    list_filter = ('status', 'category', 'listing_type', 'condition', 'created_at')
    search_fields = ('title', 'description', 'owner__email', 'owner__full_name')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
