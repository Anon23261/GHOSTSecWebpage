from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """
    Custom User model for GhostSec platform.
    Extends Django's AbstractUser to add cybersecurity platform-specific fields.
    """
    
    # Profile fields
    bio = models.TextField(_("Biography"), max_length=500, blank=True)
    avatar = models.ImageField(_("Avatar"), upload_to='avatars/%Y/%m/', null=True, blank=True)
    
    # Skill tracking
    skill_level = models.IntegerField(
        _("Skill Level"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    experience_points = models.IntegerField(
        _("Experience Points"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Security fields
    two_factor_enabled = models.BooleanField(_("Two Factor Authentication Enabled"), default=False)
    last_security_check = models.DateTimeField(_("Last Security Check"), null=True, blank=True)
    security_questions_set = models.BooleanField(_("Security Questions Set"), default=False)
    last_password_change = models.DateTimeField(_("Last Password Change"), default=timezone.now)
    failed_login_attempts = models.IntegerField(_("Failed Login Attempts"), default=0)
    account_locked_until = models.DateTimeField(_("Account Locked Until"), null=True, blank=True)
    
    # Platform engagement
    challenges_completed = models.IntegerField(_("Challenges Completed"), default=0)
    contributions = models.IntegerField(_("Community Contributions"), default=0)
    reputation_points = models.IntegerField(_("Reputation Points"), default=0)
    badges = models.JSONField(_("Earned Badges"), default=list, blank=True)
    last_active = models.DateTimeField(_("Last Active"), default=timezone.now)
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['skill_level']),
        ]
        
    def __str__(self):
        return f"{self.username} (Level {self.get_skill_level_display()})"
        
    def get_skill_level_display(self):
        """Returns the display name for the current skill level."""
        SKILL_LEVELS = {
            0: "Beginner",
            1: "Novice",
            2: "Intermediate",
            3: "Advanced",
            4: "Expert",
            5: "Master"
        }
        return SKILL_LEVELS.get(self.skill_level, "Unknown")
        
    def add_experience(self, points):
        """Add experience points and update skill level if necessary."""
        if points < 0:
            raise ValueError("Cannot add negative experience points")
        self.experience_points += points
        self._update_skill_level()
        self.save()
        
    def add_reputation(self, points):
        """Add or subtract reputation points."""
        self.reputation_points += points
        self.save()
        
    def complete_challenge(self, experience_gained):
        """Mark a challenge as completed and award experience points."""
        self.challenges_completed += 1
        self.add_experience(experience_gained)
        self.last_active = timezone.now()
        self.save()
        
    def _update_skill_level(self):
        """Update skill level based on experience points."""
        LEVEL_THRESHOLDS = [
            (0, 0),      # Beginner
            (100, 1),    # Novice
            (500, 2),    # Intermediate
            (2000, 3),   # Advanced
            (5000, 4),   # Expert
            (10000, 5),  # Master
        ]
        
        for threshold, level in LEVEL_THRESHOLDS:
            if self.experience_points < threshold:
                self.skill_level = max(0, level - 1)
                break
        else:
            self.skill_level = 5
            
    def record_login_attempt(self, successful):
        """Record a login attempt and handle account locking."""
        if successful:
            self.failed_login_attempts = 0
            self.account_locked_until = None
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
        
    def is_account_locked(self):
        """Check if the account is currently locked."""
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False
        
    def update_security_check(self):
        """Update the last security check timestamp."""
        self.last_security_check = timezone.now()
        self.save()
        
    def needs_password_change(self):
        """Check if password needs to be changed (older than 90 days)."""
        if not self.last_password_change:
            return True
        return (timezone.now() - self.last_password_change).days >= 90
