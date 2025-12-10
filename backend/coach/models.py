from django.db import models
from django.contrib.auth import get_user_model
from problems.models import Submission

User = get_user_model()


class CoachInteraction(models.Model):
    """AI Coach interaction history."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coach_interactions')
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='coach_interactions',
        null=True,
        blank=True
    )
    query = models.TextField()  # User's question or request
    response = models.TextField()  # AI coach's response
    context = models.JSONField(default=dict, blank=True)  # Additional context
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coach_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['submission']),
        ]
    
    def __str__(self):
        return f"Coach interaction for {self.user.email}"
