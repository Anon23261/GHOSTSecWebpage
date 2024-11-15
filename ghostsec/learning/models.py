from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    CATEGORY_CHOICES = [
        ('web', 'Web Security'),
        ('network', 'Network Security'),
        ('crypto', 'Cryptography'),
        ('forensics', 'Digital Forensics'),
        ('malware', 'Malware Analysis'),
        ('reverse', 'Reverse Engineering'),
        ('osint', 'OSINT'),
        ('bugbounty', 'Bug Bounty'),
        ('pentest', 'Penetration Testing'),
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

    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    enrolled_users = models.ManyToManyField(User, related_name='enrolled_courses', through='Enrollment')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    tags = models.JSONField(null=True, blank=True)
    estimated_duration = models.IntegerField(help_text='Estimated duration in hours', default=1)
    has_certificate = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('learning:course_detail', kwargs={'pk': self.pk})

class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('lab', 'Interactive Lab'),
        ('assignment', 'Assignment'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(help_text='Duration in minutes', default=30)
    resources = models.JSONField(null=True, blank=True)
    environment = models.ForeignKey('learning_environments.Environment', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completion_percentage = models.IntegerField(default=0)
    certificate_issued = models.BooleanField(default=False)
    certificate_id = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'course')
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    started = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0, help_text='Time spent in minutes')
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('enrollment', 'lesson')
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title}"

class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_number = models.CharField(max_length=100, unique=True)
    pdf_file = models.FileField(upload_to='certificates/')
    revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.enrollment.course.title}"
