from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

from listings.models import Listing

User = get_user_model()

def get_test_image():
    buf = BytesIO()
    Image.new('RGB', (100, 100), color='green').save(buf, format='JPEG')
    return SimpleUploadedFile('test.jpg', buf.getvalue(), content_type='image/jpeg')


class ListingsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(
            email='seller@campus.edu',
            password='Password123!',
            full_name='Seller Student',
            is_email_verified=True
        )
        self.buyer = User.objects.create_user(
            email='buyer@campus.edu',
            password='Password123!',
            full_name='Buyer Student',
            is_email_verified=True
        )
        self.listing = Listing.objects.create(
            owner=self.seller,
            title='Physics Textbook (10th Ed)',
            description='Comprehensive Physics for campus coursework.',
            category='Books',
            condition='Good',
            listing_type='Sell',
            price=30.00,
            status='Available',
            image=get_test_image()
        )

    def test_listing_creation_and_attributes(self):
        self.assertEqual(self.listing.title, 'Physics Textbook (10th Ed)')
        self.assertEqual(self.listing.price, 30.00)
        self.assertTrue(self.listing.is_available)

    def test_marketplace_browse_and_filtering(self):
        # Keyword search
        response = self.client.get(reverse('listings:browse') + '?q=Physics')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Physics Textbook')

        # Category filter
        response_books = self.client.get(reverse('listings:browse') + '?category=Books')
        self.assertEqual(response_books.status_code, 200)
        self.assertContains(response_books, 'Physics Textbook')

        response_cycles = self.client.get(reverse('listings:browse') + '?category=Cycles')
        self.assertEqual(response_cycles.status_code, 200)
        self.assertNotContains(response_cycles, 'Physics Textbook')

    def test_listing_crud_and_ownership_protection(self):
        # Buyer cannot edit seller's listing
        self.client.login(username='buyer@campus.edu', password='Password123!')
        forbidden_response = self.client.post(reverse('listings:edit', kwargs={'pk': self.listing.pk}), {
            'title': 'Hacked Title',
            'category': 'Books',
            'condition': 'Fair',
            'listing_type': 'Sell',
            'price': 10.00,
            'description': 'Changed'
        })
        self.assertEqual(forbidden_response.status_code, 403)

        # Seller can edit
        self.client.login(username='seller@campus.edu', password='Password123!')
        edit_response = self.client.post(reverse('listings:edit', kwargs={'pk': self.listing.pk}), {
            'title': 'Physics Textbook (Updated Edition)',
            'category': 'Books',
            'condition': 'Like New',
            'listing_type': 'Sell',
            'price': 35.00,
            'description': 'Updated description.'
        })
        self.assertEqual(edit_response.status_code, 302)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, 'Physics Textbook (Updated Edition)')
        self.assertEqual(self.listing.price, 35.00)

    def test_wishlist_functionality(self):
        self.client.login(username='buyer@campus.edu', password='Password123!')
        
        # Toggle save
        response = self.client.post(reverse('listings:wishlist_toggle', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.buyer.saved_listings.filter(pk=self.listing.pk).exists())

        # Toggle remove
        response_remove = self.client.post(reverse('listings:wishlist_toggle', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response_remove.status_code, 200)
        self.assertFalse(self.buyer.saved_listings.filter(pk=self.listing.pk).exists())
