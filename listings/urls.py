from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Marketplace Discovery
    path('', views.BrowseView.as_view(), name='browse'),
    path('create/', views.ListingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ListingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='delete'),
    path('<int:pk>/status/', views.ListingStatusToggleView.as_view(), name='status_toggle'),
    
    # Wishlist
    path('<int:pk>/wishlist-toggle/', views.WishlistToggleView.as_view(), name='wishlist_toggle'),
    path('my-wishlist/', views.WishlistView.as_view(), name='my_wishlist'),

    # Dashboard integration
    path('manage/', views.MyListingsView.as_view(), name='my_listings'),
]
