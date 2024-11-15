from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import User

@receiver(post_save, sender=User)
def update_user_security_check(sender, instance, created, **kwargs):
    """
    Signal to handle user security-related updates.
    """
    if created:
        # Set initial security check timestamp for new users
        instance.last_security_check = timezone.now()
        instance.save(update_fields=['last_security_check'])
