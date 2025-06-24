from django.test import TestCase, override_settings
from django.utils.encoding import force_str

from password_policies import forms
from tests.example import lib


class PasswordPoliciesFieldTest(TestCase):
    def test_password_field_1(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Chad+pher9k": "Chad+pher9k"},
            {"EUAdEHI3ES": ["The new password must contain 1 or more symbol."]},
        )

    def test_password_field_2(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Chad+pher9k": "Chad+pher9k"},
            {"4+53795": ["The new password must contain 3 or more letters."]},
        )

    @override_settings(PASSWORD_MIN_LOWERCASE_LETTERS=1, PASSWORD_MIN_SYMBOLS=0)
    def test_password_field_lowercase(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            valid={"Chadpher9k": "Chadpher9k"},
            invalid={
                "CHADPHER9K": [
                    "The new password must contain 1 or more lowercase letter."
                ]
            },
        )

    @override_settings(PASSWORD_MIN_UPPERCASE_LETTERS=1)
    def test_password_field_uppercase(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Chad+pher9k": "Chad+pher9k"},
            {
                "chad+pher9k": [
                    "The new password must contain 1 or more uppercase letter."
                ]
            },
        )

    def test_password_field_3(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Chad+pher9k": "Chad+pher9k"},
            {"Chad+pherg": ["The new password must contain 1 or more number."]},
        )

    def test_password_field_4(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Chad+pher9k": "Chad+pher9k"},
            {
                "aaaa5+56dddddd": [
                    "The new password contains consecutive characters. Only 3 consecutive characters are allowed.",
                    "The new password is not varied enough.",
                ]
            },
        )

    def test_password_field_5(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Chad+pher9k": "Chad+pher9k"},
            {
                "someone2@example.com": [
                    "The new password is not varied enough.",
                    "The new password is similar to an email address.",
                ]
            },
        )

    def test_password_field_6(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Ch\xc4d+pher9k": "Ch\xc4d+pher9k"},
            {
                "\xc1\xc2\xc3\xc4\u0662\xc5\xc6": [
                    "The new password must contain 1 or more symbol."
                ]
            },
        )

    def test_password_field_7(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Ch\xc4d+pher9k": "Ch\xc4d+pher9k"},
            {
                "\xc1\xc2\xc3\xc4\u0662\xc5\u20ac": [
                    "Ensure this value has at least 8 characters (it has 7)."
                ]
            },
            field_kwargs={"min_length": 8},
        )

    def test_password_field_8(self):
        from password_policies.forms.fields import PasswordPoliciesField

        self.assertFieldOutput(
            PasswordPoliciesField,
            {"Ch\xc4d+pher9k": "Ch\xc4d+pher9k"},
            {
                "a": [
                    "The new password is based on a common sequence of characters.",
                    "The new password must contain 3 or more letters.",
                    "The new password must contain 1 or more number.",
                    "The new password must contain 1 or more symbol.",
                    "The new password is not varied enough.",
                ]
            },
        )


class PasswordPoliciesFormTest(TestCase):
    def setUp(self):
        self.user = lib.create_user()
        lib.create_password_history(self.user)
        return super().setUp()

    def test_reused_password(self):
        data = {"new_password1": "ooDei1Hoo+Ru", "new_password2": "ooDei1Hoo+Ru"}
        form = forms.PasswordPoliciesForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["new_password1"].errors,
            [force_str(form.error_messages["password_used"])],
        )

    def test_password_mismatch(self):
        data = {"new_password1": "Chah+pher9k", "new_password2": "Chah+pher8k"}
        form = forms.PasswordPoliciesForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["new_password2"].errors,
            [force_str(form.error_messages["password_mismatch"])],
        )

    def test_password_verification_unicode(self):
        password = "\xc1\u20ac\xc3\xc4\u0662\xc5\xc6\xc7"
        self.assertEqual(len(password), 8)
        data = {"new_password1": password, "new_password2": password}
        form = forms.PasswordPoliciesForm(self.user, data)
        self.assertTrue(form.is_valid())

    def test_success(self):
        data = {"new_password1": "Chah+pher9k", "new_password2": "Chah+pher9k"}
        form = forms.PasswordPoliciesForm(self.user, data)
        self.assertTrue(form.is_valid())


class PasswordPoliciesChangeFormTest(TestCase):
    def setUp(self):
        self.user = lib.create_user()
        return super().setUp()

    def test_password_invalid(self):
        data = {
            "old_password": "Oor0ohf4bi",
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        form = forms.PasswordPoliciesChangeForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["old_password"].errors,
            [force_str(form.error_messages["password_incorrect"])],
        )
        self.assertFalse(form.is_valid())

    def test_success(self):
        data = {
            "old_password": lib.passwords[-1],
            "new_password1": "Chah+pher9k",
            "new_password2": "Chah+pher9k",
        }
        form = forms.PasswordPoliciesChangeForm(self.user, data)
        self.assertTrue(form.is_valid())


class PasswordResetFormTest(TestCase):
    def setUp(self):
        self.user = lib.create_user()
        return super().setUp()

    def test_unusable_password(self):
        self.user.set_unusable_password()
        self.user.save()
        data = {"email": self.user.email}
        form = forms.PasswordResetForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["email"].errors, [force_str(form.error_messages["unusable"])]
        )
        self.assertFalse(form.is_valid())

    def test_success(self):
        data = {"email": self.user.email}
        form = forms.PasswordResetForm(data)
        self.assertTrue(form.is_valid())
