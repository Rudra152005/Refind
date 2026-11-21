from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.urls import reverse

from .models import Listing
from .forms import ListingForm

class BrowseView(View):
    """Product discovery page with search, multi-faceted filters, sorting, and HTMX support."""
    def get(self, request):
        queryset = Listing.objects.filter(status='Available').select_related('owner')

        # 1. Search Query
        q = request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(category__icontains=q)
            )

        # 2. Category Filter
        category = request.GET.get('category', '').strip()
        if category and category != 'All':
            queryset = queryset.filter(category=category)

        # 3. Listing Type Filter (Sell, Exchange, Donate)
        listing_type = request.GET.get('type', '').strip()
        if listing_type and listing_type != 'All':
            queryset = queryset.filter(listing_type=listing_type)

        # 4. Condition Filter
        condition = request.GET.get('condition', '').strip()
        if condition and condition != 'All':
            queryset = queryset.filter(condition=condition)

        # 5. Price Range
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # 6. Sorting
        sort = request.GET.get('sort', 'newest')
        if sort == 'price_low':
            queryset = queryset.order_by('price', '-created_at')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price', '-created_at')
        else: # newest
            queryset = queryset.order_by('-created_at')

        # Pagination
        paginator = Paginator(queryset, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Context
        context = {
            'page_obj': page_obj,
            'total_count': queryset.count(),
            'categories': Listing.CATEGORY_CHOICES,
            'conditions': Listing.CONDITION_CHOICES,
            'listing_types': Listing.LISTING_TYPE_CHOICES,
            'selected_category': category,
            'selected_type': listing_type,
            'selected_condition': condition,
            'selected_sort': sort,
            'q': q,
            'min_price': min_price,
            'max_price': max_price,
        }

        # If HTMX partial request, return only product grid
        if request.headers.get('HX-Request'):
            return render(request, 'listings/partials/product_grid.html', context)

        return render(request, 'listings/browse.html', context)


class ListingDetailView(View):
    def get(self, request, pk):
        listing = get_object_or_404(Listing.objects.select_related('owner'), pk=pk)
        
        is_owner = request.user.is_authenticated and request.user == listing.owner
        is_saved = False
        user_offerable_listings = []

        if request.user.is_authenticated:
            is_saved = request.user.saved_listings.filter(pk=listing.pk).exists()
            # If user wants to propose exchange, fetch their own available listings
            if not is_owner and listing.listing_type == 'Exchange':
                user_offerable_listings = request.user.listings.filter(status='Available')

        # Related listings in the same category
        related_listings = Listing.objects.filter(
            category=listing.category,
            status='Available'
        ).exclude(pk=listing.pk).order_by('-created_at')[:4]

        # Check if current user already sent an active request for this listing
        existing_request = None
        if request.user.is_authenticated and not is_owner:
            from transactions.models import Request
            existing_request = Request.objects.filter(
                listing=listing,
                requester=request.user
            ).order_by('-created_at').first()

        context = {
            'listing': listing,
            'is_owner': is_owner,
            'is_saved': is_saved,
            'user_offerable_listings': user_offerable_listings,
            'related_listings': related_listings,
            'existing_request': existing_request,
        }
        return render(request, 'listings/detail.html', context)


@method_decorator(login_required, name='dispatch')
class ListingCreateView(View):
    def get(self, request):
        form = ListingForm()
        return render(request, 'listings/create.html', {'form': form})

    def post(self, request):
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.status = 'Available'
            listing.save()
            messages.success(request, f'Listing "{listing.title}" published successfully!')
            return redirect('listings:detail', pk=listing.pk)
        return render(request, 'listings/create.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ListingUpdateView(View):
    def get(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.owner != request.user and not request.user.is_staff:
            return HttpResponseForbidden("You are not authorized to edit this listing.")
        form = ListingForm(instance=listing)
        return render(request, 'listings/edit.html', {'form': form, 'listing': listing})

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.owner != request.user and not request.user.is_staff:
            return HttpResponseForbidden("You are not authorized to edit this listing.")
        
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            updated_listing = form.save(commit=False)
            if form.cleaned_data.get('clear_image2'):
                updated_listing.image2.delete(save=False)
                updated_listing.image2 = None
            if form.cleaned_data.get('clear_image3'):
                updated_listing.image3.delete(save=False)
                updated_listing.image3 = None
            updated_listing.save()
            messages.success(request, f'Listing "{updated_listing.title}" updated successfully.')
            return redirect('listings:detail', pk=updated_listing.pk)
        return render(request, 'listings/edit.html', {'form': form, 'listing': listing})


@method_decorator(login_required, name='dispatch')
class ListingDeleteView(View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.owner != request.user and not request.user.is_staff and request.user.role != 'admin':
            return HttpResponseForbidden("You are not authorized to delete this listing.")
        title = listing.title
        listing.delete()
        messages.success(request, f'Listing "{title}" has been deleted.')
        if (request.user.is_staff or request.user.role == 'admin') and listing.owner != request.user:
            return redirect('core:admin_dashboard')
        return redirect('listings:my_listings')


@method_decorator(login_required, name='dispatch')
class ListingStatusToggleView(View):
    """Allows seller or admin to mark listing as Available or Inactive/Sold."""
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.owner != request.user and not request.user.is_staff and request.user.role != 'admin':
            return HttpResponseForbidden("Unauthorized")
        
        new_status = request.POST.get('status')
        if new_status in ['Available', 'Inactive']:
            listing.status = new_status
            listing.save(update_fields=['status'])
            messages.success(request, f'Listing status changed to {new_status}.')
        referer = request.META.get('HTTP_REFERER', '')
        if str(listing.id) in referer:
            return redirect('listings:detail', pk=listing.pk)
        return redirect('listings:my_listings')


@method_decorator(login_required, name='dispatch')
class MyListingsView(View):
    def get(self, request):
        user = request.user
        status_filter = request.GET.get('status', 'all')
        
        listings_qs = user.listings.all().order_by('-created_at')
        if status_filter != 'all':
            listings_qs = listings_qs.filter(status=status_filter)

        paginator = Paginator(listings_qs, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'active_tab': 'my_listings',
            'total_listings': user.listings.count(),
            'available_count': user.listings.filter(status='Available').count(),
            'reserved_count': user.listings.filter(status='Reserved').count(),
            'completed_count': user.listings.filter(status__in=['Sold', 'Exchanged', 'Donated']).count(),
        }
        return render(request, 'listings/my_listings.html', context)


@method_decorator(login_required, name='dispatch')
class WishlistToggleView(View):
    """HTMX toggle for adding/removing a product from wishlist."""
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        user = request.user
        
        if user.saved_listings.filter(pk=listing.pk).exists():
            user.saved_listings.remove(listing)
            is_saved = False
        else:
            user.saved_listings.add(listing)
            is_saved = True

        wishlist_count = user.saved_listings.count()

        # Render button partial with updated state and trigger event
        response = render(request, 'listings/partials/wishlist_button.html', {
            'listing': listing,
            'is_saved': is_saved
        })
        response['HX-Trigger'] = f'{{"wishlistUpdated": {{"count": {wishlist_count}}}}}'
        return response


@method_decorator(login_required, name='dispatch')
class WishlistView(View):
    def get(self, request):
        saved_items = request.user.saved_listings.select_related('owner').order_by('-created_at')
        paginator = Paginator(saved_items, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'listings/wishlist.html', {
            'page_obj': page_obj,
            'active_tab': 'wishlist'
        })
