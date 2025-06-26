from django.apps import AppConfig


class ExampleConfig(AppConfig):
    app_name = "example"
    name = "Example App"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["tests.example.urls"]
