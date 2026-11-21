from django.db import models
from django.conf import settings

class Message(models.Model):
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['listing', 'sender', 'recipient']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"Msg from {self.sender.email} to {self.recipient.email} on '{self.listing.title}'"
