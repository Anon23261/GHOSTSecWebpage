from django.apps import AppConfig

class GhostSecConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec'
    verbose_name = 'GhostSec'

    def ready(self):
        """
        Initialize app when Django is ready
        """
        # Import and register signals
        try:
            import ghostsec.signals  # noqa
        except ImportError:
            pass
