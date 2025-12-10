from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CoachInteraction
from ai.services import AIService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_coach(request):
    """Chat with AI coach."""
    query = request.data.get('query')
    submission_id = request.data.get('submission_id')
    
    if not query:
        return Response(
            {'error': 'query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get context from submission if provided
    context = {'query': query}
    submission = None
    
    if submission_id:
        try:
            from problems.models import Submission
            submission = Submission.objects.get(id=submission_id, user=request.user)
            context['submission'] = {
                'code': submission.code,
                'problem': submission.problem.title,
                'error': submission.error_message,
            }
        except Submission.DoesNotExist:
            pass
    
    # Generate response using AI service
    # For MVP, we'll use a simplified version
    # In Phase 2, this will be more sophisticated
    response_text = AIService.generate_hint(
        user=request.user,
        problem_id=submission.problem.id if submission else 0,
        problem_description=query,
        user_code=submission.code if submission else None,
        error_message=submission.error_message if submission else None
    )
    
    # Save interaction
    interaction = CoachInteraction.objects.create(
        user=request.user,
        submission=submission,
        query=query,
        response=response_text,
        context=context
    )
    
    return Response({
        'response': response_text,
        'interaction_id': interaction.id
    })
