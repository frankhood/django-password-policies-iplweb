Unreleased
----------

* ``PasswordResetFormView``/``PasswordResetForm`` now default to
  ``password_policies/password_reset_email.txt`` and
  ``password_policies/password_reset_email.html`` (shipped with the package)
  instead of ``registration/password_reset_email.txt``/``.html``, which the
  package never shipped, causing ``TemplateDoesNotExist`` on the first real
  password reset email for any project that hadn't supplied its own override.
  The new default path also avoids being shadowed by
  ``django.contrib.admin``'s own ``registration/password_reset_email.html``
  (which isn't compatible with this package's 4-argument
  ``password_reset_confirm`` URL and raises ``NoReverseMatch``).
* Removed a dead ``set_usable_password`` default in
  ``PasswordPoliciesChangeForm.clean()`` that was never read anywhere.
  ``ForceChangeAdminForm``/``PasswordPoliciesAdminForm`` already support
  Django >= 5.1's real ``usable_password``/``set_usable_password`` mechanism
  out of the box, via inheritance from
  ``django.contrib.auth.forms.AdminPasswordChangeForm``; this is now covered
  by tests.

0.8.3
-----

* correct buggy behaviour on password reset

0.8.2
-----

* corrected buggy behaviour when changed password of user without PasswordProfile entry
