from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.core.exceptions import ValidationError

User = get_user_model()

class StudentRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('student', 'Campus Student (Buy, Sell, Exchange, Donate)'),
        ('admin', 'Campus Administrator / Staff (Manage & Moderate)'),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='student',
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
        }),
        label='Select Account Role'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create your password (min 6 chars)',
            'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text placeholder-muted-text focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent transition'
        }),
        min_length=6,
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your chosen password',
            'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text placeholder-muted-text focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent transition'
        }),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'role', 'phone', 'hostel']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Enter your full name',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text placeholder-muted-text focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent transition'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your.email@campus.edu or personal email',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text placeholder-muted-text focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent transition'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone number (optional)',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text placeholder-muted-text focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent transition'
            }),
            'hostel': forms.TextInput(attrs={
                'placeholder': 'Hostel / Dormitory / Hall (optional)',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text placeholder-muted-text focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent transition'
            }),
        }

    def clean_role(self):
        return self.cleaned_data.get('role') or 'student'

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists. Please log in.")

        # Check university domain if configured and not wildcard
        domains = getattr(settings, 'CAMPUS_EMAIL_DOMAINS', [])
        if domains and '*' not in domains:
            domain_part = email.split('@')[-1] if '@' in email else ''
            matches = any(domain_part == d or domain_part.endswith('.' + d) for d in domains)
            if not matches:
                domain_list = ', '.join([f"@{d}" for d in domains])
                raise ValidationError(
                    f"Please register with an email ending in: {domain_list}"
                )
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if not user.username:
            user.username = self.cleaned_data.get('email', '').strip().lower()
        role = self.cleaned_data.get('role', 'student')
        user.role = role
        if role == 'admin':
            user.is_staff = True
            user.is_email_verified = True
        else:
            user.is_email_verified = False  # Verification recommended for students
        if commit:
            user.save()
        return user


class StudentLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your registered email address',
            'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text placeholder-muted-text focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent transition'
        }),
        label='Email Address'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text placeholder-muted-text focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent transition'
        }),
        label='Password'
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label='Remember me on this browser',
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-border text-primary-green focus:ring-primary-green'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').lower().strip()
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise ValidationError("Invalid email or password. Please verify your credentials or register a new account.")
            if not user.is_active:
                raise ValidationError("This account has been deactivated. Please contact campus administration.")
            cleaned_data['user'] = user
        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone', 'hostel', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone number for handover calls/SMS',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            }),
            'hostel': forms.TextInput(attrs={
                'placeholder': 'Hostel / Dormitory / Room number',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full text-sm text-secondary-text file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-light-green file:text-primary-green hover:file:bg-accent-green hover:file:text-white transition'
            })
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size') and avatar.size > 5 * 1024 * 1024:
            raise ValidationError("Avatar image file size must not exceed 5MB.")
        return avatar
