from django.test import TestCase

# Create your tests here.
from django.test import SimpleTestCase
from django.conf import settings


class SettingsTests(SimpleTestCase):
    def test_secret_key_is_configured(self):
        self.assertTrue(settings.SECRET_KEY)

    def test_installed_apps_is_configured(self):
        self.assertTrue(settings.INSTALLED_APPS)
