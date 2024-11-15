from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec.core'
    label = 'core'
    verbose_name = 'GhostSec Core'

    def ready(self):
        try:
            import ghostsec.core.signals  # noqa
        except ImportError:
            pass
