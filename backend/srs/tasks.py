"""
Celery tasks for SRS and daily plan generation.
"""
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import DailyPlan, SRSReview
from .services import SRSService
from problems.models import Problem, Submission
from datetime import date, timedelta
import random

User = get_user_model()


@shared_task
def generate_daily_plans():
    """Generate daily plans for all users."""
    users = User.objects.all()
    for user in users:
        generate_user_daily_plan.delay(user.id)
    return f"Generated daily plans for {users.count()} users"


@shared_task
def generate_user_daily_plan(user_id):
    """Generate daily plan for a specific user."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"User {user_id} not found"
    
    today = date.today()
    plan, created = DailyPlan.objects.get_or_create(
        user=user,
        date=today,
        defaults={
            'problems': [],
            'srs_problems': [],
            'new_problems': [],
            'completed_problems': [],
        }
    )
    
    # Get 3 SRS reviews due today
    due_reviews = SRSService.get_due_reviews(user, limit=3)
    srs_problem_ids = [review.submission.problem.id for review in due_reviews]
    
    # Get 2 new problems based on user's weak patterns or random
    # For MVP, we'll select random problems
    # In Phase 2, this will use weakness mapping
    new_problems = Problem.objects.exclude(
        id__in=Submission.objects.filter(user=user).values_list('problem_id', flat=True)
    ).order_by('?')[:2]
    new_problem_ids = [p.id for p in new_problems]
    
    # Combine all problems
    all_problem_ids = srs_problem_ids + new_problem_ids
    
    plan.srs_problems = srs_problem_ids
    plan.new_problems = new_problem_ids
    plan.problems = all_problem_ids
    plan.save()
    
    return f"Generated daily plan for user {user_id} with {len(all_problem_ids)} problems"


@shared_task
def update_srs_reviews():
    """Update SRS reviews (cleanup and maintenance)."""
    # This task can be used for periodic maintenance
    # For now, it's a placeholder
    return "SRS reviews updated"

