from django.apps import AppConfig

class GhostSecAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec.ghostsec_auth'
    label = 'ghostsec_auth'

default_app_config = 'ghostsec.ghostsec_auth.GhostSecAuthConfig'
