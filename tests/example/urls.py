from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from .views import TestLoggedOutMixinView, TestHomeView

admin.site.site_header = "Example"
admin.site.site_title = "Example - Pannello amministrazione"
admin.site.index_title = "Example - Pannello amministrazione"
admin.site.enable_nav_sidebar = True
admin.site.final_catch_all_view = False


urlpatterns = [
    re_path(r"^fubar/", TestLoggedOutMixinView.as_view(), name="loggedoutmixin"),
    path("", TestHomeView.as_view(), name="home"),
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
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()