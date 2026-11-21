from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from pathlib import Path

from listings.models import Listing
from transactions.models import Request, Report
from messaging.models import Message

User = get_user_model()

class HomeView(View):
    """Attractive, modern campus marketplace landing page."""
    def get(self, request):
        available_listings = Listing.objects.filter(status='Available').select_related('owner')

        # Recently added products
        recent_listings = available_listings.order_by('-created_at')[:8]

        # Popular / Featured listings
        popular_listings = available_listings.order_by('-updated_at')[:4]

        # Category statistics
        category_counts = {}
        for cat_key, cat_label in Listing.CATEGORY_CHOICES:
            category_counts[cat_key] = Listing.objects.filter(category=cat_key, status='Available').count()

        # Sustainability metrics
        total_items_reused = Listing.objects.filter(status__in=['Sold', 'Exchanged', 'Donated']).count()
        total_active_listings = available_listings.count()
        total_students = User.objects.filter(is_active=True).count()

        context = {
            'recent_listings': recent_listings,
            'popular_listings': popular_listings,
            'category_counts': category_counts,
            'total_items_reused': total_items_reused,
            'total_active_listings': total_active_listings,
            'total_students': total_students,
        }
        return render(request, 'core/home.html', context)


class PromoVideoView(View):
    """
    Dedicated backend view that streams the promotional background video.
    Guarantees reliable serving with video/mp4 MIME type, byte-range support,
    and anti-caching headers so the browser always receives the updated video.
    """
    def get(self, request):
        candidate_paths = [
            Path(settings.BASE_DIR) / 'static' / 'videos' / 'refind-promo.mp4',
            Path(settings.BASE_DIR) / 'static' / 'videos' / 'campus-promo.mp4',
            Path(settings.BASE_DIR) / 'media' / 'videos' / 'refind-promo.mp4',
        ]
        video_file = None
        for p in candidate_paths:
            if p.exists() and p.stat().st_size > 0:
                video_file = p
                break
        
        if not video_file:
            raise Http404("Promotional video file not found on server.")
        
        response = FileResponse(open(video_file, 'rb'), content_type='video/mp4')
        response['Accept-Ranges'] = 'bytes'
        response['Cache-Control'] = 'no-cache, must-revalidate, max-age=0'
        return response


class AboutView(TemplateView):
    template_name = 'core/about.html'


class SafetyTipsView(TemplateView):
    template_name = 'core/safety.html'


def is_admin_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.role == 'admin')


@method_decorator(user_passes_test(is_admin_check, login_url='accounts:login'), name='dispatch')
class AdminStatisticsDashboardView(View):
    """
    Custom Administration Statistics & Moderation Dashboard:
    Real aggregated metrics:
    - Registered students & verified students
    - Listings breakdown (Total, Available, Sold, Exchanged, Donated)
    - Request breakdown (Total, Pending, Accepted, Completed)
    - Moderation reports (Open, Resolved, Dismissed)
    """
    def get(self, request):
        # Student metrics
        total_users = User.objects.count()
        verified_students = User.objects.filter(is_email_verified=True).count()
        active_students = User.objects.filter(is_active=True).count()

        # Listing metrics
        total_listings = Listing.objects.count()
        available_listings = Listing.objects.filter(status='Available').count()
        reserved_listings = Listing.objects.filter(status='Reserved').count()
        sold_listings = Listing.objects.filter(status='Sold').count()
        exchanged_listings = Listing.objects.filter(status='Exchanged').count()
        donated_listings = Listing.objects.filter(status='Donated').count()
        
        # Breakdown by type
        sell_type_count = Listing.objects.filter(listing_type='Sell').count()
        exchange_type_count = Listing.objects.filter(listing_type='Exchange').count()
        donate_type_count = Listing.objects.filter(listing_type='Donate').count()

        # Request metrics
        total_requests = Request.objects.count()
        pending_requests = Request.objects.filter(status='Pending').count()
        accepted_requests = Request.objects.filter(status='Accepted').count()
        completed_requests = Request.objects.filter(status='Completed').count()

        # Report moderation
        open_reports = Report.objects.filter(status='Open').select_related('listing', 'reporter', 'listing__owner').order_by('-created_at')
        total_reports = Report.objects.count()

        # Recent users
        recent_users = User.objects.order_by('-date_joined')[:5]

        context = {
            'total_users': total_users,
            'verified_students': verified_students,
            'active_students': active_students,
            'total_listings': total_listings,
            'available_listings': available_listings,
            'reserved_listings': reserved_listings,
            'sold_listings': sold_listings,
            'exchanged_listings': exchanged_listings,
            'donated_listings': donated_listings,
            'sell_type_count': sell_type_count,
            'exchange_type_count': exchange_type_count,
            'donate_type_count': donate_type_count,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'accepted_requests': accepted_requests,
            'completed_requests': completed_requests,
            'open_reports': open_reports,
            'total_reports': total_reports,
            'recent_users': recent_users,
        }
        return render(request, 'core/admin_dashboard.html', context)


@method_decorator(user_passes_test(is_admin_check, login_url='accounts:login'), name='dispatch')
class ResolveReportActionView(View):
    """Admin quick-action to mark report resolved or dismissed, or hide listing."""
    def post(self, request, report_id):
        report = get_object_or_404(Report, pk=report_id)
        action = request.POST.get('action')

        if action == 'resolve_and_hide':
            report.status = 'Resolved'
            report.save(update_fields=['status'])
            report.listing.status = 'Inactive'
            report.listing.save(update_fields=['status'])
            messages.success(request, f"Report #{report.id} resolved and listing hidden from campus marketplace.")
        elif action == 'resolve':
            report.status = 'Resolved'
            report.save(update_fields=['status'])
            messages.success(request, f"Report #{report.id} marked as resolved.")
        elif action == 'dismiss':
            report.status = 'Dismissed'
            report.save(update_fields=['status'])
            messages.info(request, f"Report #{report.id} dismissed.")

        return redirect('core:admin_dashboard')
