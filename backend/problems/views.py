from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Problem, Submission
from .serializers import ProblemSerializer, SubmissionSerializer, SubmissionCreateSerializer
from .services import Judge0Service
from srs.services import SRSService


class ProblemViewSet(viewsets.ModelViewSet):
    """ViewSet for Problem CRUD operations."""
    
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'difficulty']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def submit_code(self, request, pk=None):
        """Submit code for a problem."""
        problem = self.get_object()
        serializer = SubmissionCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Check if submission already exists
        submission, created = Submission.objects.get_or_create(
            user=request.user,
            problem=problem,
            language=serializer.validated_data['language'],
            defaults={
                'code': serializer.validated_data['code'],
                'notes': serializer.validated_data.get('notes', ''),
            }
        )
        
        if not created:
            submission.code = serializer.validated_data['code']
            submission.notes = serializer.validated_data.get('notes', '')
            submission.save()
        
        # Create SRS review if this is a solved submission
        if submission.is_solved:
            SRSService.create_review_for_submission(submission)
        
        return Response(
            SubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class SubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Submission operations."""
    
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['problem', 'language', 'is_solved', 'is_accepted']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).select_related('problem')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SubmissionCreateSerializer
        return SubmissionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        submission = serializer.instance
        if submission.is_solved:
            SRSService.create_review_for_submission(submission)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute code for a submission using Judge0."""
        submission = self.get_object()
        
        code = request.data.get('code', submission.code)
        language = request.data.get('language', submission.language)
        stdin = request.data.get('stdin')
        expected_output = request.data.get('expected_output')
        
        # Execute code
        result = Judge0Service.execute_code(
            code=code,
            language=language,
            stdin=stdin,
            expected_output=expected_output
        )
        
        # Update submission with results
        if result.get('success'):
            submission.is_accepted = result.get('is_accepted', False)
            submission.is_solved = result.get('is_accepted', False)
        else:
            submission.is_accepted = False
            submission.is_solved = False
        
        submission.runtime = result.get('runtime')
        submission.memory = result.get('memory')
        submission.error_message = result.get('error_message', '')
        submission.test_cases_passed = 1 if result.get('is_accepted') else 0
        submission.test_cases_total = 1
        submission.save()
        
        # Create SRS review if solved
        if submission.is_solved:
            SRSService.create_review_for_submission(submission)
        
        return Response(result)
