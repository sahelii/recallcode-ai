"""
GraphQL schema for RecallCode AI.
"""
import strawberry
from typing import List, Optional
from django.contrib.auth import get_user_model
from problems.models import Problem, Submission
from srs.models import SRSReview, DailyPlan
from datetime import date

User = get_user_model()


@strawberry.django.type(User)
class UserType:
    id: strawberry.ID
    username: str
    email: str
    leetcode_username: Optional[str]
    streak_count: int
    last_review_date: Optional[str]
    weakness_scores: strawberry.scalars.JSON
    created_at: str


@strawberry.django.type(Problem)
class ProblemType:
    id: strawberry.ID
    title: str
    slug: str
    description: str
    difficulty: str
    constraints: str
    examples: strawberry.scalars.JSON
    patterns: strawberry.scalars.JSON
    leetcode_id: Optional[int]
    leetcode_url: str
    created_at: str


@strawberry.django.type(Submission)
class SubmissionType:
    id: strawberry.ID
    problem: ProblemType
    code: str
    language: str
    runtime: Optional[int]
    memory: Optional[int]
    is_solved: bool
    is_accepted: bool
    notes: str
    created_at: str


@strawberry.django.type(SRSReview)
class SRSReviewType:
    id: strawberry.ID
    submission: SubmissionType
    repetitions: int
    ease_factor: float
    interval_days: int
    next_review: Optional[str]
    last_rating: Optional[int]
    total_reviews: int


@strawberry.django.type(DailyPlan)
class DailyPlanType:
    id: strawberry.ID
    date: str
    problems: strawberry.scalars.JSON
    srs_problems: strawberry.scalars.JSON
    new_problems: strawberry.scalars.JSON
    completed_problems: strawberry.scalars.JSON
    is_completed: bool


@strawberry.type
class Query:
    @strawberry.field
    def me(self, info) -> Optional[UserType]:
        """Get current authenticated user."""
        user = info.context.request.user
        if user.is_authenticated:
            return user
        return None
    
    @strawberry.field
    def daily_plan(self, info, plan_date: Optional[str] = None) -> Optional[DailyPlanType]:
        """Get daily plan for the current user."""
        user = info.context.request.user
        if not user.is_authenticated:
            return None
        
        if plan_date:
            target_date = date.fromisoformat(plan_date)
        else:
            target_date = date.today()
        
        try:
            plan = DailyPlan.objects.get(user=user, date=target_date)
            return plan
        except DailyPlan.DoesNotExist:
            return None
    
    @strawberry.field
    def problems(
        self,
        info,
        difficulty: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = 20
    ) -> List[ProblemType]:
        """Get problems with optional filtering."""
        queryset = Problem.objects.all()
        
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @strawberry.field
    def problem(self, info, id: strawberry.ID) -> Optional[ProblemType]:
        """Get a single problem by ID."""
        try:
            return Problem.objects.get(id=id)
        except Problem.DoesNotExist:
            return None
    
    @strawberry.field
    def submissions(self, info, problem_id: Optional[strawberry.ID] = None) -> List[SubmissionType]:
        """Get user's submissions."""
        user = info.context.request.user
        if not user.is_authenticated:
            return []
        
        queryset = Submission.objects.filter(user=user)
        
        if problem_id:
            queryset = queryset.filter(problem_id=problem_id)
        
        return queryset
    
    @strawberry.field
    def due_reviews(self, info, limit: Optional[int] = 10) -> List[SRSReviewType]:
        """Get due SRS reviews for the current user."""
        user = info.context.request.user
        if not user.is_authenticated:
            return []
        
        from srs.services import SRSService
        reviews = SRSService.get_due_reviews(user, limit=limit)
        return list(reviews)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_problem(
        self,
        info,
        title: str,
        description: str,
        difficulty: str,
        constraints: Optional[str] = None,
        examples: Optional[strawberry.scalars.JSON] = None,
        patterns: Optional[strawberry.scalars.JSON] = None
    ) -> ProblemType:
        """Add a new problem manually."""
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        
        problem = Problem.objects.create(
            title=title,
            description=description,
            difficulty=difficulty,
            constraints=constraints or "",
            examples=examples or [],
            patterns=patterns or []
        )
        return problem
    
    @strawberry.mutation
    def rate_review(
        self,
        info,
        review_id: strawberry.ID,
        rating: int,
        runtime: Optional[int] = None,
        memory: Optional[int] = None
    ) -> SRSReviewType:
        """Rate an SRS review."""
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        
        try:
            review = SRSReview.objects.get(id=review_id, submission__user=user)
        except SRSReview.DoesNotExist:
            raise Exception("Review not found")
        
        if not (1 <= rating <= 5):
            raise Exception("Rating must be between 1 and 5")
        
        from srs.services import SRSService
        SRSService.process_review(review, rating, runtime, memory)
        
        return review


schema = strawberry.Schema(query=Query, mutation=Mutation)


