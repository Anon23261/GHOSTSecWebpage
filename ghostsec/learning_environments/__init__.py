"""
Learning Environments Module for GhostSec
Contains isolated environments for various cybersecurity learning paths
"""

from django.apps import AppConfig

class LearningEnvironmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghostsec.learning_environments'
    label = 'learning_environments'
