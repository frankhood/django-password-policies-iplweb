from django.test import TestCase

from password_policies.models import PasswordChangeRequired, PasswordHistory
from tests.example.lib import create_password_history, create_user
from password_policies.utils import PasswordCheck


class PasswordPoliciesUtilsTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.check = PasswordCheck(self.user)
        create_password_history(self.user)
        return super().setUp()

    def test_password_check_is_required(self):
        # by default no change is required
        self.assertFalse(self.check.is_required())

        # until a change is required (usually by middleware)
        PasswordChangeRequired.objects.create(user=self.user)
        self.assertTrue(self.check.is_required())

    def test_password_check_is_expired(self):
        # `create_password_history` creates a history starting at
        # t - PASSWORD_DURATION_SECONDS, so the password is expired
        self.assertTrue(self.check.is_expired())

        # now we create a password now, so it isn't expired
        PasswordHistory.objects.create(user=self.user, password="testpass")
        self.assertFalse(self.check.is_expired())
