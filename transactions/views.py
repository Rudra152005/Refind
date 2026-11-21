from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from .models import Request, Report
from .forms import RequestForm, ReviewForm, ReportForm
from . import services
from listings.models import Listing

@method_decorator(login_required, name='dispatch')
class CreateRequestView(View):
    """Submits Buy, Exchange or Donation request for a listing."""
    def post(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)

        # Check self-request
        if listing.owner == request.user:
            messages.error(request, "You cannot request your own listing.")
            return redirect('listings:detail', pk=listing.pk)

        # Check if listing is available
        if listing.status != 'Available':
            messages.error(request, f"This listing is currently {listing.status.lower()} and cannot be requested.")
            return redirect('listings:detail', pk=listing.pk)

        # Check if already requested and pending
        existing_pending = Request.objects.filter(
            listing=listing,
            requester=request.user,
            status='Pending'
        ).exists()
        if existing_pending:
            messages.warning(request, "You already have a pending request for this listing.")
            return redirect('listings:detail', pk=listing.pk)

        message_text = request.POST.get('message', '').strip()
        offered_listing_id = request.POST.get('offered_listing')
        offered_listing = None

        if offered_listing_id and listing.listing_type == 'Exchange':
            try:
                offered_listing = Listing.objects.get(id=offered_listing_id, owner=request.user)
            except Listing.DoesNotExist:
                messages.error(request, "Selected exchange item is invalid or not owned by you.")
                return redirect('listings:detail', pk=listing.pk)

        req = Request.objects.create(
            listing=listing,
            requester=request.user,
            offered_listing=offered_listing,
            message=message_text,
            status='Pending'
        )

        messages.success(
            request,
            f"Your request for '{listing.title}' has been submitted to {listing.owner.full_name}!"
        )
        return redirect('transactions:my_requests')


@method_decorator(login_required, name='dispatch')
class MySentRequestsView(View):
    """Dashboard tab: Sent requests."""
    def get(self, request):
        user = request.user
        status_filter = request.GET.get('status', 'all')
        
        requests_qs = Request.objects.filter(requester=user).select_related('listing', 'listing__owner', 'offered_listing').order_by('-created_at')
        if status_filter != 'all':
            requests_qs = requests_qs.filter(status=status_filter)

        paginator = Paginator(requests_qs, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        review_form = ReviewForm()

        return render(request, 'transactions/my_requests.html', {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'review_form': review_form,
            'active_tab': 'my_requests'
        })


@method_decorator(login_required, name='dispatch')
class ReceivedRequestsView(View):
    """Dashboard tab: Received requests for seller's listings."""
    def get(self, request):
        user = request.user
        status_filter = request.GET.get('status', 'all')

        requests_qs = Request.objects.filter(listing__owner=user).select_related('listing', 'requester', 'offered_listing').order_by('-created_at')
        if status_filter != 'all':
            requests_qs = requests_qs.filter(status=status_filter)

        paginator = Paginator(requests_qs, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'transactions/received_requests.html', {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'active_tab': 'received_requests'
        })


@method_decorator(login_required, name='dispatch')
class AcceptRequestView(View):
    def post(self, request, pk):
        success, msg = services.accept_request(pk, request.user)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        return redirect('transactions:received_requests')


@method_decorator(login_required, name='dispatch')
class RejectRequestView(View):
    def post(self, request, pk):
        success, msg = services.reject_request(pk, request.user)
        if success:
            messages.info(request, msg)
        else:
            messages.error(request, msg)
        return redirect('transactions:received_requests')


@method_decorator(login_required, name='dispatch')
class CancelRequestView(View):
    def post(self, request, pk):
        success, msg = services.cancel_request(pk, request.user)
        if success:
            messages.info(request, msg)
        else:
            messages.error(request, msg)
        # Redirect back to where user came from
        referer = request.META.get('HTTP_REFERER', '')
        if 'received' in referer:
            return redirect('transactions:received_requests')
        return redirect('transactions:my_requests')


@method_decorator(login_required, name='dispatch')
class CompleteTransactionView(View):
    def post(self, request, pk):
        success, msg = services.complete_transaction(pk, request.user)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        return redirect('transactions:received_requests')


@method_decorator(login_required, name='dispatch')
class SubmitReviewView(View):
    def post(self, request, pk):
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text', '')
        success, msg = services.submit_review(pk, request.user, rating, review_text)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        return redirect('transactions:my_requests')


@method_decorator(login_required, name='dispatch')
class ReportListingView(View):
    def post(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "Please provide a reason for reporting this listing.")
            return redirect('listings:detail', pk=listing.pk)

        Report.objects.create(
            reporter=request.user,
            listing=listing,
            reason=reason,
            status='Open'
        )
        messages.success(request, "Listing report submitted to campus moderators for review.")
        return redirect('listings:detail', pk=listing.pk)


@method_decorator(login_required, name='dispatch')
class MyReviewsView(View):
    """Dashboard tab: Reviews received as a seller and given to other students."""
    def get(self, request):
        user = request.user
        
        # Reviews received as seller
        received_reviews = Request.objects.filter(
            listing__owner=user,
            status='Completed',
            rating__isnull=False
        ).select_related('requester', 'listing').order_by('-updated_at')

        # Reviews given by current user to sellers
        given_reviews = Request.objects.filter(
            requester=user,
            status='Completed',
            rating__isnull=False
        ).select_related('listing', 'listing__owner').order_by('-updated_at')

        return render(request, 'transactions/reviews.html', {
            'received_reviews': received_reviews,
            'given_reviews': given_reviews,
            'active_tab': 'reviews'
        })
