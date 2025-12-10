"""
SRS (Spaced Repetition System) Service
Implements custom SM-17 algorithm optimized for coding problems.
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from .models import SRSReview
from problems.models import Submission


class SRSService:
    """Service for managing SRS reviews and calculations."""
    
    # SM-17 algorithm constants
    INITIAL_EASE_FACTOR = 2.5
    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 2.5
    
    # Coding-specific adjustments
    RUNTIME_PENALTY_THRESHOLD = 0.8  # If runtime > 80% of average, apply penalty
    MEMORY_PENALTY_THRESHOLD = 0.8
    
    @staticmethod
    def calculate_next_interval(review: SRSReview, rating: int, runtime_ratio: float = 1.0, memory_ratio: float = 1.0):
        """
        Calculate next review interval using SM-17 algorithm with coding-specific adjustments.
        
        Args:
            review: SRSReview instance
            rating: User's rating (1-5)
            runtime_ratio: Ratio of user's runtime to average (for penalty)
            memory_ratio: Ratio of user's memory to average (for penalty)
        
        Returns:
            tuple: (new_interval_days, new_ease_factor)
        """
        # Base SM-17 calculation
        if rating <= 2:
            # Failed or hard - reset
            review.repetitions = 0
            review.interval_days = 1
            review.ease_factor = max(review.ease_factor - 0.2, SRSService.MIN_EASE_FACTOR)
        elif rating == 3:
            # Good
            if review.repetitions == 0:
                review.interval_days = 1
            elif review.repetitions == 1:
                review.interval_days = 6
            else:
                review.interval_days = int(review.interval_days * review.ease_factor)
            review.ease_factor = max(review.ease_factor - 0.15, SRSService.MIN_EASE_FACTOR)
        else:
            # Easy or Perfect
            if review.repetitions == 0:
                review.interval_days = 4
            elif review.repetitions == 1:
                review.interval_days = 10
            else:
                review.interval_days = int(review.interval_days * review.ease_factor)
            
            if rating == 5:
                review.ease_factor = min(review.ease_factor + 0.15, SRSService.MAX_EASE_FACTOR)
            else:
                review.ease_factor = min(review.ease_factor + 0.1, SRSService.MAX_EASE_FACTOR)
        
        # Apply coding-specific penalties
        if runtime_ratio > SRSService.RUNTIME_PENALTY_THRESHOLD:
            penalty = 1 - (runtime_ratio - SRSService.RUNTIME_PENALTY_THRESHOLD) * 0.5
            review.interval_days = max(1, int(review.interval_days * penalty))
        
        if memory_ratio > SRSService.MEMORY_PENALTY_THRESHOLD:
            penalty = 1 - (memory_ratio - SRSService.MEMORY_PENALTY_THRESHOLD) * 0.3
            review.interval_days = max(1, int(review.interval_days * penalty))
        
        # Update repetitions
        if rating >= 3:
            review.repetitions += 1
        
        return review.interval_days, review.ease_factor
    
    @staticmethod
    def process_review(review: SRSReview, rating: int, runtime: int = None, memory: int = None):
        """
        Process a review rating and update the SRS schedule.
        
        Args:
            review: SRSReview instance
            rating: User's rating (1-5)
            runtime: Code runtime in milliseconds (optional)
            memory: Code memory in KB (optional)
        """
        # Calculate runtime/memory ratios (simplified - in production, compare to average)
        runtime_ratio = 1.0
        memory_ratio = 1.0
        
        if runtime and review.submission.runtime:
            # Compare to previous submission runtime
            runtime_ratio = runtime / max(review.submission.runtime, 1)
        
        if memory and review.submission.memory:
            memory_ratio = memory / max(review.submission.memory, 1)
        
        # Calculate new interval
        interval_days, ease_factor = SRSService.calculate_next_interval(
            review, rating, runtime_ratio, memory_ratio
        )
        
        # Update review
        review.interval_days = interval_days
        review.ease_factor = ease_factor
        review.last_rating = rating
        review.last_review = timezone.now()
        review.next_review = timezone.now() + timedelta(days=interval_days)
        review.total_reviews += 1
        review.save()
        
        return review
    
    @staticmethod
    def get_due_reviews(user, limit=None):
        """
        Get all due SRS reviews for a user.
        
        Args:
            user: User instance
            limit: Maximum number of reviews to return
        
        Returns:
            QuerySet of SRSReview instances
        """
        now = timezone.now()
        reviews = SRSReview.objects.filter(
            submission__user=user,
            next_review__lte=now
        ).select_related('submission', 'submission__problem')
        
        if limit:
            reviews = reviews[:limit]
        
        return reviews
    
    @staticmethod
    def create_review_for_submission(submission: Submission):
        """
        Create an SRS review for a new submission.
        
        Args:
            submission: Submission instance
        """
        if not SRSReview.objects.filter(submission=submission).exists():
            review = SRSReview.objects.create(
                submission=submission,
                next_review=timezone.now() + timedelta(days=1),
                ease_factor=SRSService.INITIAL_EASE_FACTOR
            )
            return review
        return None

