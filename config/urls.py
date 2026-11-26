from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

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

def serve_media(request, path):
    """Serve local/fallback media files in both development and production."""
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve_media),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
