
from django import forms
from django.utils.translation import gettext_lazy as _  # noqa

from .models import PasswordChangeRequired


class PasswordChangeRequiredMixin(forms.Form):
    require_password_change = forms.BooleanField(
        initial=False,
        required=False,
        label=_("require password change"),
    )

    def save(self, commit=True):
        user = super().save(commit=commit)

        if (
            self.cleaned_data.get("require_password_change", False)
            and not PasswordChangeRequired.objects.filter(user=user).exists()
        ):
            PasswordChangeRequired.objects.create(user=user)

        return user