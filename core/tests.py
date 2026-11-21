from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from pathlib import Path

class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status_and_content(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="hero-bg-video"')
        self.assertContains(response, 'promo-video.mp4')
        self.assertContains(response, 'Give Your Pre-Loved Products a')

    def test_promo_video_backend_stream(self):
        response = self.client.get(reverse('core:promo_video'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'video/mp4')
        self.assertEqual(response.headers.get('Accept-Ranges'), 'bytes')
        self.assertIn('no-cache', response.headers.get('Cache-Control', ''))
