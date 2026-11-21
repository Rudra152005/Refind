from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Verification
    path('verify-prompt/', views.VerifyPromptView.as_view(), name='verify_prompt'),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
    path('verify-email/<str:uidb64>/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('verification-success/', views.VerificationSuccessView.as_view(), name='verification_success'),
    
    # Dashboard & Profile
    path('dashboard/', views.DashboardOverviewView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/', views.PublicProfileView.as_view(), name='public_profile'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    
    # Password Reset
    path('password-reset/', views.StudentPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.StudentPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.StudentPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.StudentPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
