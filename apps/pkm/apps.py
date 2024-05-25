from django.apps import AppConfig


class PkmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pkm'

    def ready(self):
        import apps.pkm.signals