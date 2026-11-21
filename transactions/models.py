from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Request(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )

    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='requests'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )
    offered_listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exchange_offers',
        help_text="Optional listing offered in exchange."
    )
    message = models.TextField(blank=True, help_text="Note or proposal details to the seller.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', db_index=True)
    
    # Rating and review submitted after completion
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Seller rating from 1 to 5"
    )
    review_text = models.TextField(blank=True, help_text="Feedback and experience review")
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'status']),
            models.Index(fields=['requester', 'status']),
        ]

    def __str__(self):
        return f"Request by {self.requester.full_name} for '{self.listing.title}' ({self.status})"

    def clean(self):
        super().clean()
        if self.listing and self.requester and self.listing.owner == self.requester:
            raise ValidationError("You cannot submit a request for your own listing.")

        if self.offered_listing and self.offered_listing.owner != self.requester:
            raise ValidationError("Offered exchange item must be owned by you.")


class Report(models.Model):
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Resolved', 'Resolved'),
        ('Dismissed', 'Dismissed'),
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reason = models.TextField(help_text="Explain why this listing violates campus guidelines or is inappropriate.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.pk} on '{self.listing.title}' by {self.reporter.email} ({self.status})"
