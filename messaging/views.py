from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Max
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Message
from listings.models import Listing

User = get_user_model()

@method_decorator(login_required, name='dispatch')
class InboxView(View):
    """Lists all active conversations for the authenticated student."""
    def get(self, request):
        user = request.user
        
        # Find all listings and interlocutors where user has sent or received messages
        user_messages = Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('listing', 'sender', 'recipient').order_by('-sent_at')

        # Group into conversations keyed by (listing_id, other_user_id)
        conversations = {}
        for msg in user_messages:
            other_user = msg.recipient if msg.sender == user else msg.sender
            conv_key = (msg.listing_id, other_user.id)
            if conv_key not in conversations:
                unread = Message.objects.filter(
                    listing_id=msg.listing_id,
                    sender=other_user,
                    recipient=user,
                    is_read=False
                ).count()
                conversations[conv_key] = {
                    'listing': msg.listing,
                    'other_user': other_user,
                    'last_message': msg,
                    'unread_count': unread
                }

        conversation_list = list(conversations.values())
        # Sort by latest message
        conversation_list.sort(key=lambda x: x['last_message'].sent_at, reverse=True)

        return render(request, 'messaging/inbox.html', {
            'conversations': conversation_list,
            'active_tab': 'messages'
        })


@method_decorator(login_required, name='dispatch')
class StartConversationView(View):
    """Initiates a message thread with a seller from product detail page."""
    def get(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)
        if listing.owner == request.user:
            return redirect('listings:detail', pk=listing.pk)
        return redirect('messaging:thread', listing_id=listing.id, other_user_id=listing.owner.id)


@method_decorator(login_required, name='dispatch')
class ConversationThreadView(View):
    """View and post messages within a conversation thread."""
    def get(self, request, listing_id, other_user_id):
        user = request.user
        listing = get_object_or_404(Listing, pk=listing_id)
        other_user = get_object_or_404(User, pk=other_user_id)

        # Mark all messages sent by other_user to current user as read
        Message.objects.filter(
            listing=listing,
            sender=other_user,
            recipient=user,
            is_read=False
        ).update(is_read=True)

        # Get thread messages
        messages_qs = Message.objects.filter(
            listing=listing
        ).filter(
            (Q(sender=user) & Q(recipient=other_user)) |
            (Q(sender=other_user) & Q(recipient=user))
        ).order_by('sent_at')

        context = {
            'listing': listing,
            'other_user': other_user,
            'thread_messages': messages_qs,
            'active_tab': 'messages'
        }
        return render(request, 'messaging/thread.html', context)

    def post(self, request, listing_id, other_user_id):
        user = request.user
        listing = get_object_or_404(Listing, pk=listing_id)
        other_user = get_object_or_404(User, pk=other_user_id)

        body = request.POST.get('body', '').strip()
        if body:
            new_msg = Message.objects.create(
                listing=listing,
                sender=user,
                recipient=other_user,
                body=body
            )

        if request.headers.get('HX-Request'):
            # Return partial messages list for HTMX
            messages_qs = Message.objects.filter(
                listing=listing
            ).filter(
                (Q(sender=user) & Q(recipient=other_user)) |
                (Q(sender=other_user) & Q(recipient=user))
            ).order_by('sent_at')
            return render(request, 'messaging/partials/message_list.html', {
                'thread_messages': messages_qs,
                'listing': listing,
                'other_user': other_user
            })

        return redirect('messaging:thread', listing_id=listing.id, other_user_id=other_user.id)


@method_decorator(login_required, name='dispatch')
class PollMessagesView(View):
    """HTMX polling endpoint to refresh thread messages dynamically."""
    def get(self, request, listing_id, other_user_id):
        user = request.user
        listing = get_object_or_404(Listing, pk=listing_id)
        other_user = get_object_or_404(User, pk=other_user_id)

        # Mark incoming as read
        Message.objects.filter(
            listing=listing,
            sender=other_user,
            recipient=user,
            is_read=False
        ).update(is_read=True)

        messages_qs = Message.objects.filter(
            listing=listing
        ).filter(
            (Q(sender=user) & Q(recipient=other_user)) |
            (Q(sender=other_user) & Q(recipient=user))
        ).order_by('sent_at')

        return render(request, 'messaging/partials/message_list.html', {
            'thread_messages': messages_qs,
            'listing': listing,
            'other_user': other_user
        })
