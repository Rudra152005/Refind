from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

from listings.models import Listing
from messaging.models import Message

User = get_user_model()

def get_test_image():
    buf = BytesIO()
    Image.new('RGB', (100, 100), color='green').save(buf, format='JPEG')
    return SimpleUploadedFile('test.jpg', buf.getvalue(), content_type='image/jpeg')


class MessagingTest(TestCase):
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
            title='Desk Lamp',
            description='Warm LED desk lamp.',
            category='Hostel Essentials',
            condition='Like New',
            listing_type='Sell',
            price=15.00,
            status='Available',
            image=get_test_image()
        )

    def test_send_and_retrieve_messages(self):
        self.client.login(username='buyer@campus.edu', password='Password123!')
        
        # Post message to thread
        thread_url = reverse('messaging:thread', kwargs={
            'listing_id': self.listing.id,
            'other_user_id': self.seller.id
        })
        response = self.client.post(thread_url, {
            'body': 'Hello! Is this lamp still available?'
        })
        self.assertEqual(response.status_code, 302)

        # Verify DB
        msg = Message.objects.filter(listing=self.listing, sender=self.buyer, recipient=self.seller).first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.body, 'Hello! Is this lamp still available?')
        self.assertFalse(msg.is_read)

        # Seller logs in and views thread with the buyer (marking message as read)
        self.client.login(username='seller@campus.edu', password='Password123!')
        seller_thread_url = reverse('messaging:thread', kwargs={
            'listing_id': self.listing.id,
            'other_user_id': self.buyer.id
        })
        thread_view_response = self.client.get(seller_thread_url)
        self.assertEqual(thread_view_response.status_code, 200)
        self.assertContains(thread_view_response, 'Hello! Is this lamp still available?')

        msg.refresh_from_db()
        self.assertTrue(msg.is_read)
