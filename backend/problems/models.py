from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Problem(models.Model):
    """Problem model for storing coding problems."""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    constraints = models.TextField(blank=True)
    examples = models.JSONField(default=list, blank=True)
    patterns = models.JSONField(default=list, blank=True)  # e.g., ["Two Pointers", "Sliding Window"]
    leetcode_id = models.IntegerField(null=True, blank=True, unique=True)
    leetcode_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'problems'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['leetcode_id']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Submission(models.Model):
    """User's code submission for a problem."""
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('go', 'Go'),
        ('rust', 'Rust'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python')
    runtime = models.IntegerField(null=True, blank=True)  # in milliseconds
    memory = models.IntegerField(null=True, blank=True)  # in KB
    is_solved = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    test_cases_passed = models.IntegerField(default=0)
    test_cases_total = models.IntegerField(default=0)
    notes = models.TextField(blank=True)  # Markdown notes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'problem']),
            models.Index(fields=['is_solved']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['user', 'problem', 'language']]
    
    def __str__(self):
        return f"{self.user.email} - {self.problem.title}"
