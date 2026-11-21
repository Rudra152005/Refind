from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator

from .forms import StudentRegistrationForm, StudentLoginForm, UserProfileUpdateForm
from .services import send_verification_email, verify_email_token
from .models import User

class StudentPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'emails/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')

class StudentPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class StudentPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class StudentPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = StudentRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                success, verify_url, code = send_verification_email(request, user)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(
                    request,
                    f"Welcome to ReFind, {user.full_name}! A 6-digit verification code has been sent to {user.email}."
                )
                # Store verification code & URL in session for seamless dev preview
                request.session['dev_verification_url'] = verify_url
                request.session['dev_verification_code'] = code
                return redirect('accounts:verify_prompt')
            except Exception as e:
                import logging
                logging.getLogger(__name__).exception("Registration processing failed: %s", e)
                messages.error(request, f"Could not complete registration: {e}")
                return render(request, 'accounts/register.html', {'form': form})
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = StudentLoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            remember_me = form.cleaned_data.get('remember_me', True)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)  # 2 weeks session
            messages.success(request, f"Welcome back, {user.full_name}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.role == 'admin':
                return redirect('core:admin_dashboard')
            return redirect('accounts:dashboard')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('core:home')

    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('core:home')


class VerifyPromptView(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_email_verified:
            return redirect('accounts:dashboard')
        
        dev_url = request.session.get('dev_verification_url')
        dev_code = request.session.get('dev_verification_code') or request.user.verification_code
        if not dev_code and not request.user.is_email_verified:
            _, dev_url, dev_code = send_verification_email(request, request.user)
            request.session['dev_verification_url'] = dev_url
            request.session['dev_verification_code'] = dev_code

        return render(request, 'accounts/verify_prompt.html', {
            'dev_verification_url': dev_url,
            'dev_verification_code': dev_code,
        })


class VerifyCodeView(View):
    @method_decorator(login_required)
    def post(self, request):
        if request.user.is_email_verified:
            return redirect('accounts:dashboard')
        
        entered_code = request.POST.get('code', '').strip()
        user = request.user

        if user.verification_code and user.verification_code == entered_code:
            user.is_email_verified = True
            user.verification_code = None
            user.save(update_fields=['is_email_verified', 'verification_code'])
            request.session.pop('dev_verification_url', None)
            request.session.pop('dev_verification_code', None)
            messages.success(request, "Campus email successfully verified! You now have full access.")
            return redirect('accounts:verification_success')
        else:
            messages.error(request, "Invalid or incorrect 6-digit verification code. Please check and try again.")
            return redirect('accounts:verify_prompt')


class ResendVerificationView(View):
    @method_decorator(login_required)
    def post(self, request):
        if request.user.is_email_verified:
            messages.info(request, "Your email is already verified.")
            return redirect('accounts:dashboard')
        success, verify_url, code = send_verification_email(request, request.user)
        request.session['dev_verification_url'] = verify_url
        request.session['dev_verification_code'] = code
        messages.success(request, f"A fresh 6-digit verification code has been sent to {request.user.email}.")
        return redirect('accounts:verify_prompt')


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        user = verify_email_token(uidb64, token)
        if user:
            messages.success(request, "Your student campus email has been successfully verified! You now have full access.")
            if not request.user.is_authenticated:
                login(request, user)
            return redirect('accounts:verification_success')
        else:
            messages.error(request, "The verification link is invalid or has expired.")
            return render(request, 'accounts/verify_failed.html')


class VerificationSuccessView(TemplateView):
    template_name = 'accounts/verification_success.html'


@method_decorator(login_required, name='dispatch')
class DashboardOverviewView(View):
    def get(self, request):
        user = request.user
        
        # User listings
        listings = user.listings.all().order_by('-created_at')
        total_listings = listings.count()
        active_listings = listings.filter(status='Available').count()
        sold_listings = listings.filter(status__in=['Sold', 'Exchanged', 'Donated']).count()
        
        # Requests
        from transactions.models import Request
        sent_pending_requests = Request.objects.filter(requester=user, status='Pending').count()
        received_pending_requests = Request.objects.filter(listing__owner=user, status='Pending').count()
        
        # Messaging
        from messaging.models import Message
        unread_messages = Message.objects.filter(recipient=user, is_read=False).count()
        
        # Recent items for quick preview
        recent_listings = listings[:5]
        recent_received_requests = Request.objects.filter(listing__owner=user).select_related('requester', 'listing').order_by('-created_at')[:5]

        context = {
            'total_listings': total_listings,
            'active_listings': active_listings,
            'sold_listings': sold_listings,
            'sent_pending_requests': sent_pending_requests,
            'received_pending_requests': received_pending_requests,
            'unread_messages': unread_messages,
            'recent_listings': recent_listings,
            'recent_received_requests': recent_received_requests,
            'active_tab': 'overview'
        }
        return render(request, 'accounts/dashboard_overview.html', context)


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        user = request.user
        form = UserProfileUpdateForm(instance=user)
        return render(request, 'accounts/profile.html', {
            'form': form,
            'active_tab': 'profile'
        })

    def post(self, request):
        user = request.user
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
        return render(request, 'accounts/profile.html', {
            'form': form,
            'active_tab': 'profile'
        })


@method_decorator(login_required, name='dispatch')
class PublicProfileView(View):
    """View another student's public profile and seller stats."""
    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk)
        available_listings = student.listings.filter(status='Available').order_by('-created_at')
        
        # Reviews
        from transactions.models import Request
        reviews = Request.objects.filter(
            listing__owner=student,
            status='Completed',
            rating__isnull=False
        ).select_related('requester', 'listing').order_by('-updated_at')

        return render(request, 'accounts/public_profile.html', {
            'student': student,
            'listings': available_listings,
            'reviews': reviews
        })


@method_decorator(login_required, name='dispatch')
class SettingsView(View):
    def get(self, request):
        password_form = PasswordChangeForm(request.user)
        return render(request, 'accounts/settings.html', {
            'password_form': password_form,
            'active_tab': 'settings'
        })

    def post(self, request):
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('accounts:settings')
        return render(request, 'accounts/settings.html', {
            'password_form': password_form,
            'active_tab': 'settings'
        })
