from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date
from .models import SRSReview, DailyPlan
from .services import SRSService
from problems.models import Submission


class SRSReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SRS Review operations."""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SRSReview.objects.filter(
            submission__user=self.request.user
        ).select_related('submission', 'submission__problem')
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a review (1-5) and update SRS schedule."""
        review = self.get_object()
        rating = request.data.get('rating')
        runtime = request.data.get('runtime')
        memory = request.data.get('memory')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response(
                {'error': 'Rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating = int(rating)
        SRSService.process_review(review, rating, runtime, memory)
        
        # Update user streak if this is today's first review
        user = request.user
        if user.last_review_date != timezone.now().date():
            user.update_streak()
        
        return Response({
            'message': 'Review rated successfully',
            'next_review': review.next_review,
            'interval_days': review.interval_days,
        })
    
    @action(detail=False, methods=['get'])
    def due(self, request):
        """Get all due reviews for the current user."""
        reviews = SRSService.get_due_reviews(request.user, limit=10)
        data = []
        for review in reviews:
            data.append({
                'id': review.id,
                'problem': {
                    'id': review.submission.problem.id,
                    'title': review.submission.problem.title,
                    'slug': review.submission.problem.slug,
                    'difficulty': review.submission.problem.difficulty,
                },
                'submission_id': review.submission.id,
                'next_review': review.next_review,
                'interval_days': review.interval_days,
                'repetitions': review.repetitions,
                'ease_factor': review.ease_factor,
            })
        return Response(data)


class DailyPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Daily Plan operations."""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DailyPlan.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's daily plan."""
        today = date.today()
        plan, created = DailyPlan.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'problems': [], 'srs_problems': [], 'new_problems': []}
        )
        
        # If plan is empty, generate it
        if not plan.problems:
            from .tasks import generate_user_daily_plan
            generate_user_daily_plan(request.user.id)
            plan.refresh_from_db()
        
        return Response({
            'id': plan.id,
            'date': plan.date,
            'problems': plan.problems,
            'srs_problems': plan.srs_problems,
            'new_problems': plan.new_problems,
            'completed_problems': plan.completed_problems,
            'is_completed': plan.is_completed,
        })
    
    @action(detail=True, methods=['post'])
    def complete_problem(self, request, pk=None):
        """Mark a problem as completed in the daily plan."""
        plan = self.get_object()
        problem_id = request.data.get('problem_id')
        
        if not problem_id:
            return Response(
                {'error': 'problem_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if problem_id not in plan.completed_problems:
            plan.completed_problems.append(problem_id)
            plan.save()
        
        # Check if all problems are completed
        total_problems = len(plan.problems)
        if len(plan.completed_problems) >= total_problems:
            plan.is_completed = True
            plan.save()
        
        return Response({
            'completed_problems': plan.completed_problems,
            'is_completed': plan.is_completed,
        })
