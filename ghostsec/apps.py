from django.apps import AppConfig

class GhostSecConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec'
    verbose_name = 'GhostSec'

    def ready(self):
        """
        Initialize app when Django is ready
        """
        try:
            # Import signals
            import ghostsec.signals
        except ImportError:
            pass
