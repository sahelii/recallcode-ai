from django.contrib.auth.models import AbstractUser
from django.db import models
import json


class User(AbstractUser):
    """Custom User model with LeetCode integration and weakness tracking."""
    
    email = models.EmailField(unique=True)
    leetcode_username = models.CharField(max_length=100, blank=True, null=True)
    weakness_scores = models.JSONField(default=dict, blank=True)
    streak_count = models.IntegerField(default=0)
    last_review_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['leetcode_username']),
        ]
    
    def __str__(self):
        return self.email
    
    def update_streak(self):
        """Update user's streak count based on daily reviews."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_review_date:
            days_diff = (today - self.last_review_date).days
            if days_diff == 1:
                self.streak_count += 1
            elif days_diff > 1:
                self.streak_count = 1
        else:
            self.streak_count = 1
        
        self.last_review_date = today
        self.save()