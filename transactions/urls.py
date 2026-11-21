from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Request Submission
    path('request/<int:listing_id>/', views.CreateRequestView.as_view(), name='create_request'),
    
    # Request Management
    path('my-requests/', views.MySentRequestsView.as_view(), name='my_requests'),
    path('received-requests/', views.ReceivedRequestsView.as_view(), name='received_requests'),
    
    # Lifecycle actions
    path('requests/<int:pk>/accept/', views.AcceptRequestView.as_view(), name='accept_request'),
    path('requests/<int:pk>/reject/', views.RejectRequestView.as_view(), name='reject_request'),
    path('requests/<int:pk>/cancel/', views.CancelRequestView.as_view(), name='cancel_request'),
    path('requests/<int:pk>/complete/', views.CompleteTransactionView.as_view(), name='complete_transaction'),
    
    # Reviews
    path('requests/<int:pk>/review/', views.SubmitReviewView.as_view(), name='submit_review'),
    path('reviews/', views.MyReviewsView.as_view(), name='my_reviews'),
    
    # Reporting
    path('report/<int:listing_id>/', views.ReportListingView.as_view(), name='report_listing'),
]
