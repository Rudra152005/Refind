from io import BytesIO
import tempfile
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from core.storage import ResilientMediaStorage


def _make_test_image(name='test.jpg'):
    buf = BytesIO()
    Image.new('RGB', (40, 40), color='green').save(buf, format='JPEG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/jpeg')


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


class ResilientMediaStorageTest(TestCase):
    def test_cloudinary_upload_failure_falls_back_to_local_and_serves_in_prod(self):
        with tempfile.TemporaryDirectory() as tmp_media:
            with override_settings(
                DEBUG=False,
                MEDIA_ROOT=tmp_media,
                USE_CLOUDINARY=True,
                CLOUDINARY_CLOUD_NAME='demo',
                IS_TESTING=False,
                INSTALLED_APPS=[*settings.INSTALLED_APPS, 'cloudinary_storage'],
            ):
                storage = ResilientMediaStorage()
                mock_cloud = MagicMock()
                mock_cloud._save.side_effect = RuntimeError('Request forbidden due to missing permissions')
                mock_cloud.delete.side_effect = RuntimeError('Delete forbidden')
                mock_cloud.exists.return_value = False

                with patch.object(storage, '_get_cloudinary_storage', return_value=mock_cloud):
                    img = _make_test_image('very_long_' + ('x' * 120) + '.jpg')
                    safe_name = storage.get_available_name(f'listings/{img.name}', max_length=500)
                    self.assertLessEqual(len(safe_name), 85)

                    saved_name = storage.save(safe_name, img)
                    self.assertTrue(storage.exists(saved_name))
                    url = storage.url(saved_name)
                    self.assertTrue(url.startswith('/media/'))

                    # Verify production URL routing serves /media/ even with DEBUG=False
                    resp = self.client.get(url)
                    self.assertEqual(resp.status_code, 200)
                    resp.close()

                    # Delete should work locally and also swallow remote errors gracefully
                    storage.delete(saved_name)
                    self.assertFalse(storage.exists(saved_name))
                    storage.delete('media/nonexistent_remote_id')
