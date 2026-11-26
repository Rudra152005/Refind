import importlib
import logging
import os
from pathlib import PurePosixPath

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible

logger = logging.getLogger(__name__)


@deconstructible
class ResilientMediaStorage(Storage):
    """
    Media storage backend that uses Cloudinary when enabled and reachable,
    and automatically falls back to local MEDIA_ROOT storage if Cloudinary
    uploads fail (e.g., restricted API key permissions or network errors).
    """

    def __init__(self, location=None, base_url=None):
        self._location = location
        self._base_url = base_url
        self._local_storage = None
        self._cloudinary_storage = None

    @property
    def local_storage(self):
        target_location = self._location or settings.MEDIA_ROOT
        target_base_url = self._base_url or settings.MEDIA_URL
        if (
            self._local_storage is None
            or self._local_storage.location != os.fspath(target_location)
            or self._local_storage.base_url != target_base_url
        ):
            self._local_storage = FileSystemStorage(
                location=target_location,
                base_url=target_base_url,
            )
        return self._local_storage

    def _is_cloudinary_enabled(self):
        return (
            getattr(settings, 'USE_CLOUDINARY', False)
            and bool(getattr(settings, 'CLOUDINARY_CLOUD_NAME', ''))
            and not getattr(settings, 'IS_TESTING', False)
            and 'cloudinary_storage' in getattr(settings, 'INSTALLED_APPS', [])
        )

    def _get_cloudinary_storage(self):
        if self._cloudinary_storage is None:
            module = importlib.import_module('cloudinary_storage.storage')
            self._cloudinary_storage = module.MediaCloudinaryStorage()
        return self._cloudinary_storage

    @staticmethod
    def _truncate_name(name, max_length):
        name = name.replace('\\', '/')
        if not max_length or len(name) <= max_length:
            return name
        path = PurePosixPath(name)
        parent = '' if str(path.parent) == '.' else f"{path.parent}/"
        ext = path.suffix
        stem = path.stem
        available_stem = max(1, max_length - len(parent) - len(ext))
        return f"{parent}{stem[:available_stem]}{ext}"

    def get_available_name(self, name, max_length=None):
        # Leave headroom for Cloudinary's media/ prefix and suffix to avoid DB varchar overflow
        safe_limit = min(max_length, 85) if max_length else 85
        name = self._truncate_name(name, safe_limit)
        if not self._is_cloudinary_enabled():
            return self.local_storage.get_available_name(name, max_length=max_length)
        return name

    def _open(self, name, mode='rb'):
        if self.local_storage.exists(name):
            return self.local_storage.open(name, mode)
        if self._is_cloudinary_enabled():
            return self._get_cloudinary_storage()._open(name, mode)
        return self.local_storage.open(name, mode)

    def _save(self, name, content):
        name = name.replace('\\', '/')
        if hasattr(content, 'seek'):
            try:
                content.seek(0)
            except Exception:
                pass

        if self._is_cloudinary_enabled():
            try:
                return self._get_cloudinary_storage()._save(name, content)
            except Exception as exc:
                logger.warning(
                    "Cloudinary upload failed for '%s' (%s). Falling back to local media storage.",
                    name,
                    exc,
                )
                if hasattr(content, 'seek'):
                    try:
                        content.seek(0)
                    except Exception:
                        pass

        return self.local_storage.save(name, content)

    def delete(self, name):
        if not name:
            return
        if self.local_storage.exists(name):
            self.local_storage.delete(name)
            return
        if self._is_cloudinary_enabled():
            try:
                self._get_cloudinary_storage().delete(name)
            except Exception as exc:
                logger.warning("Cloudinary delete failed for '%s': %s", name, exc)

    def exists(self, name):
        if not name:
            return False
        if self.local_storage.exists(name):
            return True
        if self._is_cloudinary_enabled():
            try:
                return self._get_cloudinary_storage().exists(name)
            except Exception as exc:
                logger.warning("Cloudinary exists check failed for '%s': %s", name, exc)
                return False
        return False

    def size(self, name):
        if self.local_storage.exists(name):
            return self.local_storage.size(name)
        if self._is_cloudinary_enabled():
            try:
                return self._get_cloudinary_storage().size(name)
            except Exception as exc:
                logger.warning("Cloudinary size check failed for '%s': %s", name, exc)
                return None
        return None

    def url(self, name):
        if not name:
            return ''
        if self.local_storage.exists(name):
            return self.local_storage.url(name)
        if self._is_cloudinary_enabled():
            try:
                return self._get_cloudinary_storage().url(name)
            except Exception as exc:
                logger.warning("Cloudinary URL generation failed for '%s': %s", name, exc)
        return self.local_storage.url(name)

    def path(self, name):
        return self.local_storage.path(name)
