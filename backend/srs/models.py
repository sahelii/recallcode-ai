from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from problems.models import Submission

User = get_user_model()


class SRSReview(models.Model):
    """Spaced Repetition System review tracking."""
    
    RATING_CHOICES = [
        (1, 'Again - Hard'),
        (2, 'Hard'),
        (3, 'Good'),
        (4, 'Easy'),
        (5, 'Perfect'),
    ]
    
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='srs_review'
    )
    repetitions = models.IntegerField(default=0)  # Number of successful reviews
    ease_factor = models.FloatField(default=2.5)  # SM-17 ease factor
    interval_days = models.IntegerField(default=1)  # Days until next review
    next_review = models.DateTimeField(null=True, blank=True)
    last_review = models.DateTimeField(null=True, blank=True)
    last_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'srs_reviews'
        ordering = ['next_review']
        indexes = [
            models.Index(fields=['next_review']),
            models.Index(fields=['submission']),
        ]
    
    def __str__(self):
        return f"SRS Review for {self.submission.problem.title}"
    
    def is_due(self):
        """Check if this review is due."""
        if not self.next_review:
            return True
        return timezone.now() >= self.next_review


class DailyPlan(models.Model):
    """Daily practice plan for a user."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_plans')
    date = models.DateField()
    problems = models.JSONField(default=list)  # List of problem IDs
    srs_problems = models.JSONField(default=list)  # List of SRS review IDs
    new_problems = models.JSONField(default=list)  # List of new problem IDs
    completed_problems = models.JSONField(default=list)  # List of completed problem IDs
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_plans'
        unique_together = [['user', 'date']]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Daily Plan for {self.user.email} on {self.date}"
