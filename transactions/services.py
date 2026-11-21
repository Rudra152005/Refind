from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Request, Report
from listings.models import Listing

def accept_request(request_id, current_user):
    """
    Accepts a student request with database concurrency protection:
    1. Starts a database transaction.
    2. Locks the listing row with select_for_update().
    3. Verifies listing is still Available and request is Pending.
    4. Sets request to Accepted and listing to Reserved.
    5. Automatically rejects all other pending requests for this listing.
    """
    with transaction.atomic():
        try:
            req = Request.objects.select_related('listing').get(id=request_id)
        except Request.DoesNotExist:
            return False, "Request does not exist."

        # Lock listing row
        listing = Listing.objects.select_for_update().get(id=req.listing_id)

        # Authorization check: only listing owner can accept
        if listing.owner != current_user:
            return False, "You are not authorized to accept requests for this listing."

        # State check
        if listing.status != 'Available':
            return False, f"Listing is no longer available (current status: {listing.status})."

        if req.status != 'Pending':
            return False, f"Request cannot be accepted because its status is {req.status}."

        # Accept selected request
        req.status = 'Accepted'
        req.save(update_fields=['status', 'updated_at'])

        # Mark listing as Reserved
        listing.status = 'Reserved'
        listing.save(update_fields=['status', 'updated_at'])

        # Concurrently reject all other pending requests for this listing
        Request.objects.filter(
            listing=listing,
            status='Pending'
        ).exclude(id=req.id).update(status='Rejected', updated_at=timezone.now())

        return True, f"Request from {req.requester.full_name} accepted. The item is now reserved."


def complete_transaction(request_id, current_user):
    """
    Marks handover as completed:
    1. Sets request to Completed.
    2. Updates listing status to Sold, Exchanged, or Donated depending on its listing_type.
    """
    with transaction.atomic():
        try:
            req = Request.objects.select_related('listing').get(id=request_id)
        except Request.DoesNotExist:
            return False, "Request does not exist."

        listing = Listing.objects.select_for_update().get(id=req.listing_id)

        # Check authorization (seller or requester can confirm completion)
        if listing.owner != current_user and req.requester != current_user:
            return False, "Unauthorized."

        if req.status != 'Accepted':
            return False, "Only accepted requests can be completed."

        req.status = 'Completed'
        req.save(update_fields=['status', 'updated_at'])

        if listing.listing_type == 'Sell':
            listing.status = 'Sold'
        elif listing.listing_type == 'Exchange':
            listing.status = 'Exchanged'
            # If an offered listing was exchanged, mark it Exchanged too
            if req.offered_listing:
                Listing.objects.filter(id=req.offered_listing_id).update(status='Exchanged')
        elif listing.listing_type == 'Donate':
            listing.status = 'Donated'
        else:
            listing.status = 'Sold'

        listing.save(update_fields=['status', 'updated_at'])

        return True, "Handover completed successfully! Thank you for reusing campus goods."


def reject_request(request_id, current_user):
    """Seller rejects a pending request."""
    try:
        req = Request.objects.select_related('listing').get(id=request_id)
    except Request.DoesNotExist:
        return False, "Request does not exist."

    if req.listing.owner != current_user:
        return False, "Unauthorized."

    if req.status != 'Pending':
        return False, "Only pending requests can be rejected."

    req.status = 'Rejected'
    req.save(update_fields=['status', 'updated_at'])
    return True, "Request rejected."


def cancel_request(request_id, current_user):
    """
    Requester cancels pending request, OR either party cancels accepted request.
    If an accepted request is cancelled, listing status returns to Available!
    """
    with transaction.atomic():
        try:
            req = Request.objects.select_related('listing').get(id=request_id)
        except Request.DoesNotExist:
            return False, "Request does not exist."

        listing = Listing.objects.select_for_update().get(id=req.listing_id)

        is_requester = req.requester == current_user
        is_seller = listing.owner == current_user

        if not (is_requester or is_seller):
            return False, "Unauthorized."

        if req.status not in ['Pending', 'Accepted']:
            return False, f"Cannot cancel a request with status {req.status}."

        was_accepted = (req.status == 'Accepted')
        req.status = 'Cancelled'
        req.save(update_fields=['status', 'updated_at'])

        # If it was accepted and reserved, return listing to Available
        if was_accepted and listing.status == 'Reserved':
            listing.status = 'Available'
            listing.save(update_fields=['status', 'updated_at'])

        return True, "Request cancelled."


def submit_review(request_id, current_user, rating, review_text):
    """Allows requester to rate and review seller after completion."""
    try:
        req = Request.objects.select_related('listing').get(id=request_id)
    except Request.DoesNotExist:
        return False, "Request does not exist."

    if req.requester != current_user:
        return False, "Only the requester can rate the seller."

    if req.status != 'Completed':
        return False, "You can only review a completed transaction."

    if req.rating is not None:
        return False, "A review has already been submitted for this transaction."

    try:
        rating_int = int(rating)
        if not (1 <= rating_int <= 5):
            return False, "Rating must be between 1 and 5 stars."
    except (ValueError, TypeError):
        return False, "Invalid rating value."

    req.rating = rating_int
    req.review_text = review_text.strip()
    req.save(update_fields=['rating', 'review_text', 'updated_at'])

    return True, "Thank you! Your seller rating and review have been recorded."
