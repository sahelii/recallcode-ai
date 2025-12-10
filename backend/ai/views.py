from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import AIService
from problems.models import Problem, Submission


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_hint(request):
    """Generate AI hint for a problem."""
    problem_id = request.data.get('problem_id')
    submission_id = request.data.get('submission_id')
    
    if not problem_id:
        return Response(
            {'error': 'problem_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        problem = Problem.objects.get(id=problem_id)
    except Problem.DoesNotExist:
        return Response(
            {'error': 'Problem not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user_code = None
    error_message = None
    
    if submission_id:
        try:
            submission = Submission.objects.get(id=submission_id, user=request.user)
            user_code = submission.code
            if submission.error_message:
                error_message = submission.error_message
        except Submission.DoesNotExist:
            pass
    
    hint = AIService.generate_hint(
        user=request.user,
        problem_id=problem_id,
        problem_description=problem.description,
        user_code=user_code,
        error_message=error_message
    )
    
    return Response({'hint': hint})
