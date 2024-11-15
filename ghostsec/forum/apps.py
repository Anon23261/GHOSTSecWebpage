from django.apps import AppConfig

class ForumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec.forum'
    label = 'forum'
    verbose_name = 'Forum'