from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class CTFChallenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    CATEGORY_CHOICES = [
        ('web', 'Web Security'),
        ('crypto', 'Cryptography'),
        ('forensics', 'Digital Forensics'),
        ('pwn', 'Binary Exploitation'),
        ('reverse', 'Reverse Engineering'),
        ('misc', 'Miscellaneous'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    flag = models.CharField(max_length=200)
    points = models.IntegerField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.title} ({self.category} - {self.difficulty})"

class CTFHint(models.Model):
    challenge = models.ForeignKey(CTFChallenge, on_delete=models.CASCADE, related_name='hints')
    content = models.TextField()
    cost = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Hint for {self.challenge.title}"

class CTFScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(CTFChallenge, on_delete=models.CASCADE)
    solved_at = models.DateTimeField(default=timezone.now)
    points_earned = models.IntegerField()
    
    class Meta:
        unique_together = ('user', 'challenge')
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.points_earned} points)"
