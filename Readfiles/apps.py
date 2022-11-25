from django.apps import AppConfig


class ReadfilesConfig(AppConfig):
    name = 'Readfiles'

    def ready(self):
        import Readfiles.signals
