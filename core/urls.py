from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('promo-video.mp4', views.PromoVideoView.as_view(), name='promo_video'),
    path('promo-video/', views.PromoVideoView.as_view(), name='promo_video_alt'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('safety-guidelines/', views.SafetyTipsView.as_view(), name='safety'),
    
    # Custom Administration Statistics & Moderation
    path('administration/dashboard/', views.AdminStatisticsDashboardView.as_view(), name='admin_dashboard'),
    path('administration/reports/<int:report_id>/action/', views.ResolveReportActionView.as_view(), name='report_action'),
]
