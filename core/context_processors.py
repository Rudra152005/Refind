from listings.models import Listing
from messaging.models import Message
from transactions.models import Request

def global_context(request):
    """Provides global context to all Django templates."""
    context = {
        'SITE_NAME': 'ReFind',
        'SITE_TAGLINE': 'Find it again. Give it a new beginning.',
        'CAMPUS_NAME': 'University Community',
        'CATEGORY_CHOICES': Listing.CATEGORY_CHOICES,
        'wishlist_count': 0,
        'unread_messages_count': 0,
        'pending_received_requests_count': 0,
    }

    if request.user.is_authenticated:
        try:
            context['wishlist_count'] = request.user.saved_listings.count()
            context['unread_messages_count'] = Message.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
            context['pending_received_requests_count'] = Request.objects.filter(
                listing__owner=request.user,
                status='Pending'
            ).count()
        except Exception:
            pass

    return context
