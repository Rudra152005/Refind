from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg

class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifiers for auth."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model representing verified campus students and administrators."""
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Administrator'),
    )

    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(_('campus email address'), unique=True, db_index=True)
    full_name = models.CharField(_('full name'), max_length=150)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    hostel = models.CharField(_('hostel / hall of residence'), max_length=100, blank=True)
    avatar = models.ImageField(_('avatar image'), upload_to='avatars/', max_length=500, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_email_verified = models.BooleanField(_('email verified'), default=False)
    verification_code = models.CharField(_('verification code'), max_length=6, blank=True, null=True)
    
    # Wishlist ManyToMany relationship to Listing
    saved_listings = models.ManyToManyField(
        'listings.Listing',
        related_name='saved_by',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        """Calculate average seller rating from completed requests across owned listings."""
        from transactions.models import Request
        avg_val = Request.objects.filter(
            listing__owner=self,
            status='Completed',
            rating__isnull=False
        ).aggregate(avg=Avg('rating'))['avg']
        return round(avg_val, 1) if avg_val else None

    @property
    def total_ratings_count(self):
        """Count how many ratings the user has received."""
        from transactions.models import Request
        return Request.objects.filter(
            listing__owner=self,
            status='Completed',
            rating__isnull=False
        ).count()

    @property
    def completed_transactions_count(self):
        """Count completed transactions where this user was the seller."""
        from transactions.models import Request
        return Request.objects.filter(
            listing__owner=self,
            status='Completed'
        ).count()

    @property
    def active_listings_count(self):
        """Count active available listings owned by user."""
        return self.listings.filter(status='Available').count()
