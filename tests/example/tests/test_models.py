from django.test import TestCase

from password_policies.conf import settings
from password_policies.models import PasswordHistory
from tests.example import lib


class PasswordHistoryModelTestCase(TestCase):
    def setUp(self):
        self.user = lib.create_user()
        lib.create_password_history(self.user)
        return super().setUp()

    def test_password_history_expiration_with_offset(self):
        offset = settings.PASSWORD_HISTORY_COUNT + 2
        PasswordHistory.objects.delete_expired(self.user, offset=offset)
        count = PasswordHistory.objects.filter(user=self.user).count()
        self.assertEqual(count, offset)

    def test_password_history_expiration(self):
        PasswordHistory.objects.delete_expired(self.user)
        count = PasswordHistory.objects.filter(user=self.user).count()
        self.assertEqual(count, settings.PASSWORD_HISTORY_COUNT)

    def test_password_history_recent_passwords(self):
        self.assertFalse(
            PasswordHistory.objects.check_password(self.user, lib.passwords[-1])
        )
