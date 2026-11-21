from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Core & Marketplace Public Views
    path('', include('core.urls', namespace='core')),

    # Accounts & Authentication
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Product Listings
    path('listings/', include('listings.urls', namespace='listings')),

    # Transactions & Requests
    path('transactions/', include('transactions.urls', namespace='transactions')),

    # Messaging System
    path('messages/', include('messaging.urls', namespace='messaging')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
