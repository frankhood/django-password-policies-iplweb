from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from password_policies.views import LoggedOutMixin


class TestHomeView(View):
    def get(self, request):
        return HttpResponse(
            "<html><head><title>Home</title></head><body><p>Welcome!</p></body></html>"
        )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TestLoggedOutMixinView(LoggedOutMixin):
    pass
