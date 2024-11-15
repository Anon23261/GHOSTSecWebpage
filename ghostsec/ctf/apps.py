from django.apps import AppConfig

class CTFConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec.ctf'
    label = 'ctf'
    verbose_name = 'CTF'
