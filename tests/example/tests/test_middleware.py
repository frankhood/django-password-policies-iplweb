from urllib.parse import urljoin

from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

from password_policies.conf import settings
from password_policies.models import PasswordChangeRequired, PasswordHistory
from tests.example import lib


def get_response_location(location):
    if not location.startswith("http://testserver/"):
        location = urljoin("http://testserver/", location)
    return location


class PasswordPoliciesMiddlewareTest(TestCase):
    def setUp(self):
        self.user = lib.create_user()
        self.redirect_url = "http://testserver/admin/password/change/?next=/"

    def test_password_middleware_without_history(self):
        seconds = settings.PASSWORD_DURATION_SECONDS - 60
        self.user.date_joined = lib.get_datetime_from_delta(timezone.now(), seconds)
        self.user.last_login = lib.get_datetime_from_delta(timezone.now(), seconds)
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_password_middleware_with_history(self):
        lib.create_password_history(self.user)
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()
        PasswordHistory.objects.filter(user=self.user).delete()

    def test_password_middleware_enforced_redirect(self):
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()

    def test_password_change_required_enforced_redirect(self):
        seconds = settings.PASSWORD_DURATION_SECONDS - 60
        self.user.date_joined = lib.get_datetime_from_delta(timezone.now(), seconds)
        self.user.last_login = lib.get_datetime_from_delta(timezone.now(), seconds)
        self.user.save()
        p = PasswordChangeRequired.objects.create(user=self.user)
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()
        p.delete()

    # @override_settings(PASSWORD_CHECK_ONLY_FOR_STAFF_USERS=False)  # default
    def test_password_change_required_if_not_staff_user_and_not_PASSWORD_CHECK_ONLY_FOR_STAFF_USERS(
        self,
    ):
        self.user.is_staff = False
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()

    @override_settings(PASSWORD_CHECK_ONLY_FOR_STAFF_USERS=True)
    def test_password_change_not_required_if_not_staff_user_and_PASSWORD_CHECK_ONLY_FOR_STAFF_USERS(
        self,
    ):
        self.user.is_staff = False
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    # @override_settings(PASSWORD_CHECK_ONLY_FOR_STAFF_USERS=False)  # default
    def test_password_change_required_if_staff_user_and_not_PASSWORD_CHECK_ONLY_FOR_STAFF_USERS(
        self,
    ):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()

    @override_settings(PASSWORD_CHECK_ONLY_FOR_STAFF_USERS=True)  # default
    def test_password_change_not_required_if_staff_user_and_PASSWORD_CHECK_ONLY_FOR_STAFF_USERS(
        self,
    ):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()


@override_settings(
    SESSION_SERIALIZER="django.contrib.sessions.serializers.JSONSerializer"
)
class PasswordPoliciesMiddlewareJsonSerializerTest(TestCase):
    def setUp(self):
        self.user = lib.create_user()
        self.redirect_url = "http://testserver/admin/password/change/?next=/"

    def test_password_middleware_without_history(self):
        seconds = settings.PASSWORD_DURATION_SECONDS - 60
        self.user.date_joined = lib.get_datetime_from_delta(timezone.now(), seconds)
        self.user.last_login = lib.get_datetime_from_delta(timezone.now(), seconds)
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_password_middleware_with_history(self):
        lib.create_password_history(self.user)
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()
        PasswordHistory.objects.filter(user=self.user).delete()

    def test_password_middleware_enforced_redirect(self):
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()

    def test_password_change_required_enforced_redirect(self):
        seconds = settings.PASSWORD_DURATION_SECONDS - 60
        self.user.date_joined = lib.get_datetime_from_delta(timezone.now(), seconds)
        self.user.last_login = lib.get_datetime_from_delta(timezone.now(), seconds)
        self.user.save()
        p = PasswordChangeRequired.objects.create(user=self.user)
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()
        p.delete()

    # @override_settings(PASSWORD_CHECK_ONLY_FOR_STAFF_USERS=False)  # default
    def test_password_change_required_if_not_staff_user_and_not_PASSWORD_CHECK_ONLY_FOR_STAFF_USERS(
        self,
    ):
        self.user.is_staff = False
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()

    @override_settings(PASSWORD_CHECK_ONLY_FOR_STAFF_USERS=True)
    def test_password_change_not_required_if_not_staff_user_and_PASSWORD_CHECK_ONLY_FOR_STAFF_USERS(
        self,
    ):
        self.user.is_staff = False
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    # @override_settings(PASSWORD_CHECK_ONLY_FOR_STAFF_USERS=False)  # default
    def test_password_change_required_if_staff_user_and_not_PASSWORD_CHECK_ONLY_FOR_STAFF_USERS(
        self,
    ):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()

    @override_settings(PASSWORD_CHECK_ONLY_FOR_STAFF_USERS=True)  # default
    def test_password_change_not_required_if_staff_user_and_PASSWORD_CHECK_ONLY_FOR_STAFF_USERS(
        self,
    ):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="alice", password=lib.passwords[-1])
        response = self.client.get(reverse("home"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_response_location(response["Location"]), self.redirect_url)
        self.client.logout()
