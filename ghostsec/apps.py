from django.apps import AppConfig

class GhostSecConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec'
    
    def ready(self):
        try:
            import ghostsec.signals  # noqa
        except ImportError:
            pass
