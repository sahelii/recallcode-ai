from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AIHint(models.Model):
    """AI-generated hints for problems."""
    
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('groq', 'Groq'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_hints')
    problem_id = models.IntegerField()  # Problem ID
    hint = models.TextField()
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='openai')
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_hints'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'problem_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"AI Hint for Problem {self.problem_id}"
