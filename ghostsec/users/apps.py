from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec.users'
    verbose_name = 'Users'

    def ready(self):
        try:
            import ghostsec.users.signals  # noqa
        except ImportError:
            pass
