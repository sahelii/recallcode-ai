from rest_framework import serializers
from .models import Problem, Submission


class ProblemSerializer(serializers.ModelSerializer):
    """Serializer for Problem model."""
    
    class Meta:
        model = Problem
        fields = (
            'id', 'title', 'slug', 'description', 'difficulty',
            'constraints', 'examples', 'patterns', 'leetcode_id',
            'leetcode_url', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model."""
    
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    problem_slug = serializers.CharField(source='problem.slug', read_only=True)
    problem_difficulty = serializers.CharField(source='problem.difficulty', read_only=True)
    
    class Meta:
        model = Submission
        fields = (
            'id', 'problem', 'problem_title', 'problem_slug', 'problem_difficulty',
            'code', 'language', 'runtime', 'memory', 'is_solved', 'is_accepted',
            'error_message', 'test_cases_passed', 'test_cases_total', 'notes',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new submission."""
    
    class Meta:
        model = Submission
        fields = ('problem', 'code', 'language', 'notes')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

