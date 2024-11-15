from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

class Environment(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
    ]
    
    TYPE_CHOICES = [
        ('web', 'Web Application Security'),
        ('network', 'Network Security'),
        ('malware', 'Malware Analysis'),
        ('forensics', 'Digital Forensics'),
        ('cloud', 'Cloud Security'),
        ('bugbounty', 'Bug Bounty'),
        ('pentest', 'Penetration Testing'),
        ('reverse', 'Reverse Engineering'),
        ('programming', 'Programming'),
        ('linux', 'Linux Security'),
    ]
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('csharp', 'C#'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('assembly', 'Assembly'),
        ('bash', 'Bash/Shell'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    max_time = models.IntegerField(help_text='Maximum time in minutes')
    max_instances = models.IntegerField(default=1)
    current_instances = models.IntegerField(default=0)
    is_sandbox = models.BooleanField(default=False)
    sandbox_config = models.JSONField(null=True, blank=True)
    memory_limit = models.IntegerField(help_text='Memory limit in MB', default=512)
    cpu_limit = models.IntegerField(help_text='CPU limit in percentage', default=50)
    disk_limit = models.IntegerField(help_text='Disk space limit in MB', default=1024)
    network_enabled = models.BooleanField(default=True)
    custom_tools = models.JSONField(null=True, blank=True, help_text='List of custom tools available in the environment')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('learning_environments:environment_detail', kwargs={'pk': self.pk})

class EnvironmentInstance(models.Model):
    STATUS_CHOICES = [
        ('starting', 'Starting'),
        ('running', 'Running'),
        ('stopping', 'Stopping'),
        ('stopped', 'Stopped'),
        ('error', 'Error'),
    ]

    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='instances')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='starting')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    resource_id = models.CharField(max_length=100, null=True, blank=True)
    current_memory = models.IntegerField(help_text='Current memory usage in MB', null=True)
    current_cpu = models.IntegerField(help_text='Current CPU usage in percentage', null=True)
    current_disk = models.IntegerField(help_text='Current disk usage in MB', null=True)
    logs = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.environment.name} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=self.environment.max_time)
        super().save(*args, **kwargs)

class EnvironmentAccess(models.Model):
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='access_granted')
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='access_revoked')
    
    class Meta:
        unique_together = ('environment', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.environment.name}"

class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    TYPE_CHOICES = [
        ('bugbounty', 'Bug Bounty'),
        ('pentest', 'Penetration Testing'),
        ('code_review', 'Code Review'),
        ('exploit_dev', 'Exploit Development'),
        ('reverse_eng', 'Reverse Engineering'),
        ('forensics', 'Digital Forensics'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    points = models.IntegerField(default=0)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='challenges')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    flag = models.CharField(max_length=200)
    hints = models.JSONField(null=True, blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    def __str__(self):
        return self.name

class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect'),
    ]

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    flag = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attempts = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ('challenge', 'user', 'flag')
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.name}"
