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
        "admin/password_change/",
        RedirectView.as_view(pattern_name="password_change", permanent=False),
    ),
    path("admin/password/", include("password_policies.urls")),
```

## Credits
---

Strumenti utilizzati per la creazione di questo package:

* [Cookiecutter](https://github.com/audreyr/cookiecutter)
* [cookiecutter-djangopackage](https://github.com/pydanny/cookiecutter-djangopackage)
