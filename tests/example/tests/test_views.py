from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls.base import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from freezegun import freeze_time
from rest_framework import status

from password_policies.conf import settings
from password_policies.forms import (
    PasswordPoliciesChangeForm,
    PasswordResetForm,
)
from password_policies.models import PasswordHistory
from tests.example.lib import create_user, passwords
from password_policies.utils import datetime_to_string, string_to_datetime


class PasswordChangeViewsTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        return super().setUp()

    def test_password_change(self):
        """
        A ``GET`` to the ``password_change`` view uses the appropriate
        template and populates the password change form into the context.
        """
        self.client.login(username="alice", password=passwords[-1])
        response = self.client.get(reverse("password_change"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            isinstance(response.context["form"], PasswordPoliciesChangeForm)
        )
        self.assertTemplateUsed(response, "registration/password_change_form.html")
        self.client.logout()

    def test_password_change_failure(self):
        """
        A ``POST`` to the ``password_change`` view with invalid data properly
        fails and issues the according error.
        """
        data = {
            "old_password": "password",
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        msg = "Your old password was entered incorrectly. Please enter it again."
        self.client.login(username="alice", password=passwords[-1])
        response = self.client.post(reverse("password_change"), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(response.context["form"].errors["old_password"], [msg])
        self.client.logout()

    def test_password_change_success(self):
        """
        A ``POST`` to the ``change_email_create`` view with valid data properly
        changes the user's password, creates a new password history entry
        for the user and issues a redirect.
        """
        data = {
            "old_password": passwords[-1],
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        self.client.login(username="alice", password=data["old_password"])
        response = self.client.post(reverse("password_change"), data=data)
        self.assertEqual(PasswordHistory.objects.count(), 1)
        obj = PasswordHistory.objects.get()
        self.assertTrue(response.url.endswith(reverse("password_change_done")))
        obj.delete()
        self.client.logout()

    @override_settings(
        SESSION_SERIALIZER="django.contrib.sessions.serializers.JSONSerializer",
        USE_TZ=False,
    )
    @freeze_time("2021-07-21T17:00:00.000000")
    def test_pickle_serializer_set_datetime_USE_TZ_false(self):
        data = {
            "old_password": passwords[-1],
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        self.client.login(username="alice", password=data["old_password"])
        self.client.post(reverse("password_change"), data=data)
        session = self.client.session

        # Assert session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            "2021-07-21T17:00:00.000000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
            ),
            timezone.now(),
        )
        # Assert session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            "2021-07-21T17:00:00.000000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
            ),
            timezone.now(),
        )

    @override_settings(
        SESSION_SERIALIZER="django.contrib.sessions.serializers.JSONSerializer",
        USE_TZ=True,
    )
    @freeze_time("2021-07-21T17:00:00.000000")
    def test_pickle_serializer_set_datetime_USE_TZ_true(self):
        data = {
            "old_password": passwords[-1],
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        self.client.login(username="alice", password=data["old_password"])
        self.client.post(reverse("password_change"), data=data)
        session = self.client.session

        # Assert session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            "2021-07-21T17:00:00.000000+0000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
            ),
            timezone.now(),
        )
        # Assert session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            "2021-07-21T17:00:00.000000+0000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
            ),
            timezone.now(),
        )

    @override_settings(
        SESSION_SERIALIZER="django.contrib.sessions.serializers.JSONSerializer",
        USE_TZ=True,
    )
    @freeze_time("2021-07-21T18:00:00.000000+0100")
    def test_pickle_serializer_set_datetime_USE_TZ_true_localized(self):
        data = {
            "old_password": passwords[-1],
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        self.client.login(username="alice", password=data["old_password"])
        self.client.post(reverse("password_change"), data=data)
        session = self.client.session

        # Assert session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            "2021-07-21T17:00:00.000000+0000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
            ),
            timezone.now(),
        )
        # Assert session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            "2021-07-21T17:00:00.000000+0000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
            ),
            timezone.now(),
        )

    @override_settings(
        SESSION_SERIALIZER="django.contrib.sessions.serializers.JSONSerializer",
        USE_TZ=False,
    )
    @freeze_time("2021-07-21T17:00:00.000000")
    def test_json_serializer_set_datetime_USE_TZ_false(self):
        data = {
            "old_password": passwords[-1],
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        self.client.login(username="alice", password=data["old_password"])
        self.client.post(reverse("password_change"), data=data)
        session = self.client.session

        # Assert session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            "2021-07-21T17:00:00.000000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
            ),
            timezone.now(),
        )
        # Assert session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            "2021-07-21T17:00:00.000000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
            ),
            timezone.now(),
        )

    @override_settings(
        SESSION_SERIALIZER="django.contrib.sessions.serializers.JSONSerializer",
        USE_TZ=True,
    )
    @freeze_time("2021-07-21T17:00:00.000000")
    def test_json_serializer_set_datetime_USE_TZ_true(self):
        data = {
            "old_password": passwords[-1],
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        self.client.login(username="alice", password=data["old_password"])
        self.client.post(reverse("password_change"), data=data)
        session = self.client.session

        # Assert session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            "2021-07-21T17:00:00.000000+0000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
            ),
            timezone.now(),
        )
        # Assert session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            "2021-07-21T17:00:00.000000+0000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
            ),
            timezone.now(),
        )

    @override_settings(
        SESSION_SERIALIZER="django.contrib.sessions.serializers.JSONSerializer",
        USE_TZ=True,
    )
    @freeze_time("2021-07-21T18:00:00.000000+0100")
    def test_json_serializer_set_datetime_USE_TZ_true_localized(self):
        data = {
            "old_password": passwords[-1],
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        self.client.login(username="alice", password=data["old_password"])
        self.client.post(reverse("password_change"), data=data)
        session = self.client.session

        # Assert session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY],
            "2021-07-21T17:00:00.000000+0000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHECKED_SESSION_KEY]
            ),
            timezone.now(),
        )
        # Assert session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
        self.assertIsInstance(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY], str
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            datetime_to_string(timezone.now()),
        )
        self.assertEqual(
            session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY],
            "2021-07-21T17:00:00.000000+0000",
        )
        self.assertEqual(
            string_to_datetime(
                session[settings.PASSWORD_POLICIES_LAST_CHANGED_SESSION_KEY]
            ),
            timezone.now(),
        )


class PasswordResetFormViewTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        return super().setUp()

    def test_get_ok(self):
        response = self.client.get(reverse("admin_password_reset"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.context["form"], PasswordResetForm))
        self.assertTemplateUsed(response, "registration/password_reset_form.html")

    def test_post_ok(self):
        data = {"email": self.user.email}
        response = self.client.post(reverse("admin_password_reset"), data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse("password_reset_done"))

    def test_post_not_ok(self):
        data = {"email": "emailnotok@gmail.com"}
        response = self.client.post(reverse("admin_password_reset"), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetDoneViewTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        return super().setUp()

    def test_get_ok(self):
        response = self.client.get(reverse("password_reset_done"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "registration/password_reset_done.html")


class PasswordResetConfirmViewTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        self.signer = signing.TimestampSigner()
        self.var = self.signer.sign(self.user.password).split(":")
        return super().setUp()

    def test_get_ok(self):
        response = self.client.get(
            reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": urlsafe_base64_encode(force_bytes(self.user.id)),
                    "token": default_token_generator.make_token(self.user),
                    "timestamp": self.var[1],
                    "signature": self.var[2],
                },
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "registration/password_reset_confirm.html")

    def test_post_ok(self):
        data = {
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }

        response = self.client.post(
            reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": urlsafe_base64_encode(force_bytes(self.user.id)),
                    "token": default_token_generator.make_token(self.user),
                    "timestamp": self.var[1],
                    "signature": self.var[2],
                },
            ),
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse("password_reset_complete"))

    def test_post_not_ok(self):
        data = {
            "new_password1": "badpwd",
            "new_password2": "badpwd",
        }

        response = self.client.post(
            reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": urlsafe_base64_encode(force_bytes(self.user.id)),
                    "token": default_token_generator.make_token(self.user),
                    "timestamp": self.var[1],
                    "signature": self.var[2],
                },
            ),
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetCompleteViewTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        return super().setUp()

    def test_get_ok(self):
        response = self.client.get(reverse("password_reset_complete"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "registration/password_reset_complete.html")


class TestLOMixinView(TestCase):
    def test_lomixinview(self):
        c = Client()
        c.get(reverse("loggedoutmixin"))
