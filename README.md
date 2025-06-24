# django-password-policies

``django-password-policies-iplweb`` is an application for the `Django`_ framework that
provides unicode-aware password policies on password changes and resets and a
mechanism to force password changes.


## Documentation

The full documentation is at http://github.com/iplweb/django-password-policies-iplweb


## Quickstart

Install `django-password-policies-iplweb`:

```shell
    pip install django-password-policies-iplweb
```

Add it at the END of your `INSTALLED_APPS`:

```python
    INSTALLED_APPS = (
        ...
        'password_policies',
    )
```

Add django-password-policies-iplweb's URL patterns:

```python
    path(
        "password_change/",
        RedirectView.as_view(pattern_name="password_change", permanent=False),
    ),
    path(
        "admin/",
        include(
            [
                path("", admin.site.urls),
                path("password/", include("password_policies.urls")),
            ]
        ),
    ),
```

Add in your project/templates/registration password_reset_email.html and password_reset_email.txt like files in tests/example/templates/registration.

The link "Forgotten your password or username?" in admin was generated creating url with name "admin_password_reset".

## Credits
---

Tools for create this package:

* [Cookiecutter](https://github.com/audreyr/cookiecutter)
* [cookiecutter-djangopackage](https://github.com/pydanny/cookiecutter-djangopackage)
