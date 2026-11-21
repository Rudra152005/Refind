from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse

class Listing(models.Model):
    CATEGORY_CHOICES = (
        ('Books', 'Books & Academic Materials'),
        ('Electronics', 'Laptops & Electronics'),
        ('Furniture', 'Furniture & Study Desks'),
        ('Cycles', 'Bicycles & Campus Transport'),
        ('Sports', 'Sports Equipment'),
        ('Hostel Essentials', 'Hostel Essentials'),
        ('Other', 'Other Student Essentials'),
    )

    CONDITION_CHOICES = (
        ('New', 'Brand New'),
        ('Like New', 'Like New'),
        ('Good', 'Good Condition'),
        ('Fair', 'Fair / Usable'),
    )

    LISTING_TYPE_CHOICES = (
        ('Sell', 'Sell (Cash on Campus)'),
        ('Exchange', 'Exchange / Barter'),
        ('Donate', 'Free / Donate to Student'),
    )

    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Reserved', 'Reserved / Pending Handover'),
        ('Sold', 'Sold'),
        ('Exchanged', 'Exchanged'),
        ('Donated', 'Donated'),
        ('Inactive', 'Inactive / Hidden'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, db_index=True)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    wanted_item_text = models.TextField(
        blank=True,
        help_text="For exchange listings: describe what goods you would like to receive in return."
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available', db_index=True)
    
    # Up to 3 images (first image mandatory)
    image = models.ImageField(upload_to='listings/')
    image2 = models.ImageField(upload_to='listings/', blank=True, null=True)
    image3 = models.ImageField(upload_to='listings/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['status', 'listing_type']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.listing_type} - {self.status})"

    def clean(self):
        super().clean()
        # Price validation
        if self.listing_type == 'Sell':
            if self.price is None or self.price <= 0:
                raise ValidationError({'price': 'A price greater than 0 is required for items listed for sale.'})
        elif self.listing_type == 'Donate':
            self.price = 0.00
        elif self.listing_type == 'Exchange':
            self.price = 0.00

    def get_absolute_url(self):
        return reverse('listings:detail', kwargs={'pk': self.pk})

    @property
    def is_available(self):
        return self.status == 'Available'

    @property
    def is_sold_or_closed(self):
        return self.status in ['Sold', 'Exchanged', 'Donated']

    @property
    def all_images(self):
        """Return list of valid existing images for the listing gallery."""
        imgs = []
        if self.image:
            imgs.append(self.image)
        if self.image2:
            imgs.append(self.image2)
        if self.image3:
            imgs.append(self.image3)
        return imgs
