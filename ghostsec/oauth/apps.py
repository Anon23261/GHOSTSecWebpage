from django.apps import AppConfig

class OAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec.oauth'
    label = 'oauth'
    verbose_name = 'OAuth'
