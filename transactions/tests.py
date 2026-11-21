from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

from listings.models import Listing
from transactions.models import Request, Report
from transactions import services

User = get_user_model()

def get_test_image():
    buf = BytesIO()
    Image.new('RGB', (100, 100), color='green').save(buf, format='JPEG')
    return SimpleUploadedFile('test.jpg', buf.getvalue(), content_type='image/jpeg')


class TransactionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(
            email='seller@campus.edu',
            password='Password123!',
            full_name='Seller Student',
            is_email_verified=True
        )
        self.buyer1 = User.objects.create_user(
            email='buyer1@campus.edu',
            password='Password123!',
            full_name='Buyer One',
            is_email_verified=True
        )
        self.buyer2 = User.objects.create_user(
            email='buyer2@campus.edu',
            password='Password123!',
            full_name='Buyer Two',
            is_email_verified=True
        )
        self.listing = Listing.objects.create(
            owner=self.seller,
            title='Engineering Calculator',
            description='Barely used scientific calculator.',
            category='Electronics',
            condition='Like New',
            listing_type='Sell',
            price=25.00,
            status='Available',
            image=get_test_image()
        )

    def test_create_request_and_self_request_prevention(self):
        # Seller cannot request own listing
        self.client.login(username='seller@campus.edu', password='Password123!')
        res_self = self.client.post(reverse('transactions:create_request', kwargs={'listing_id': self.listing.id}), {
            'message': 'Buying my own item'
        })
        self.assertFalse(Request.objects.filter(listing=self.listing, requester=self.seller).exists())

        # Buyer can request
        self.client.login(username='buyer1@campus.edu', password='Password123!')
        res_buyer = self.client.post(reverse('transactions:create_request', kwargs={'listing_id': self.listing.id}), {
            'message': 'Can we meet at the cafeteria at 3 PM?'
        })
        self.assertEqual(res_buyer.status_code, 302)
        self.assertTrue(Request.objects.filter(listing=self.listing, requester=self.buyer1).exists())

    def test_double_acceptance_prevention_and_concurrency_protection(self):
        """
        Critical business requirement:
        When a seller accepts request A:
        1. Request A status becomes Accepted.
        2. Listing status becomes Reserved.
        3. Request B is automatically Rejected.
        """
        # Create two competing pending requests
        req_a = Request.objects.create(
            listing=self.listing,
            requester=self.buyer1,
            message='Offer from Buyer 1',
            status='Pending'
        )
        req_b = Request.objects.create(
            listing=self.listing,
            requester=self.buyer2,
            message='Offer from Buyer 2',
            status='Pending'
        )

        # Seller accepts Request A via service
        success, msg = services.accept_request(req_a.id, self.seller)
        self.assertTrue(success)

        # Refresh states from DB
        req_a.refresh_from_db()
        req_b.refresh_from_db()
        self.listing.refresh_from_db()

        self.assertEqual(req_a.status, 'Accepted')
        self.assertEqual(self.listing.status, 'Reserved')
        self.assertEqual(req_b.status, 'Rejected', "Compromising pending request must be automatically rejected!")

        # Attempting to accept Request B must now fail
        success_b, msg_b = services.accept_request(req_b.id, self.seller)
        self.assertFalse(success_b)

    def test_complete_transaction_and_review(self):
        req = Request.objects.create(
            listing=self.listing,
            requester=self.buyer1,
            status='Accepted'
        )
        self.listing.status = 'Reserved'
        self.listing.save()

        # Complete handover
        success, msg = services.complete_transaction(req.id, self.seller)
        self.assertTrue(success)

        req.refresh_from_db()
        self.listing.refresh_from_db()

        self.assertEqual(req.status, 'Completed')
        self.assertEqual(self.listing.status, 'Sold')

        # Requester submits 5-star review
        rev_success, rev_msg = services.submit_review(
            req.id,
            self.buyer1,
            rating=5,
            review_text="Fantastic seller, item as described!"
        )
        self.assertTrue(rev_success)
        req.refresh_from_db()
        self.assertEqual(req.rating, 5)
        self.assertEqual(req.review_text, "Fantastic seller, item as described!")

        # Check seller average rating calculation
        self.assertEqual(self.seller.average_rating, 5.0)

    def test_listing_reporting(self):
        self.client.login(username='buyer1@campus.edu', password='Password123!')
        response = self.client.post(reverse('transactions:report_listing', kwargs={'listing_id': self.listing.id}), {
            'reason': 'Inappropriate listing content testing.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Report.objects.filter(listing=self.listing, reporter=self.buyer1).exists())
