"""
AI Service for generating hints and coaching.
Supports multiple AI providers: OpenAI, Anthropic, Groq.
"""
import os
from django.conf import settings
from .models import AIHint


class AIService:
    """Service for AI-powered hints and coaching."""
    
    @staticmethod
    def get_provider():
        """Get the configured AI provider."""
        return getattr(settings, 'AI_PROVIDER', 'openai')
    
    @staticmethod
    def generate_hint(user, problem_id, problem_description, user_code=None, error_message=None):
        """
        Generate an AI hint for a problem.
        
        Args:
            user: User instance
            problem_id: Problem ID
            problem_description: Problem description
            user_code: User's code (optional)
            error_message: Error message if any (optional)
        
        Returns:
            str: AI-generated hint
        """
        provider = AIService.get_provider()
        
        # Build context
        context = {
            'problem_description': problem_description,
        }
        if user_code:
            context['user_code'] = user_code
        if error_message:
            context['error_message'] = error_message
        
        # Generate hint based on provider
        if provider == 'openai':
            hint = AIService._generate_openai_hint(context)
        elif provider == 'anthropic':
            hint = AIService._generate_anthropic_hint(context)
        elif provider == 'groq':
            hint = AIService._generate_groq_hint(context)
        else:
            hint = "AI hint generation is not configured."
        
        # Save hint
        AIHint.objects.create(
            user=user,
            problem_id=problem_id,
            hint=hint,
            provider=provider,
            context=context
        )
        
        return hint
    
    @staticmethod
    def _generate_openai_hint(context):
        """Generate hint using OpenAI."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            prompt = f"""You are a coding coach helping a developer solve a problem.

Problem Description:
{context.get('problem_description', '')}

"""
            if context.get('user_code'):
                prompt += f"""User's Current Code:
{context['user_code']}

"""
            if context.get('error_message'):
                prompt += f"""Error Message:
{context['error_message']}

"""
            prompt += """Provide a helpful hint (not the full solution) that guides the developer toward the solution. 
Keep it concise and educational."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful coding coach."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating hint: {str(e)}"
    
    @staticmethod
    def _generate_anthropic_hint(context):
        """Generate hint using Anthropic Claude."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            prompt = f"""You are a coding coach helping a developer solve a problem.

Problem Description:
{context.get('problem_description', '')}

"""
            if context.get('user_code'):
                prompt += f"""User's Current Code:
{context['user_code']}

"""
            if context.get('error_message'):
                prompt += f"""Error Message:
{context['error_message']}

"""
            prompt += """Provide a helpful hint (not the full solution) that guides the developer toward the solution. 
Keep it concise and educational."""

            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=200,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating hint: {str(e)}"
    
    @staticmethod
    def _generate_groq_hint(context):
        """Generate hint using Groq."""
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            prompt = f"""You are a coding coach helping a developer solve a problem.

Problem Description:
{context.get('problem_description', '')}

"""
            if context.get('user_code'):
                prompt += f"""User's Current Code:
{context['user_code']}

"""
            if context.get('error_message'):
                prompt += f"""Error Message:
{context['error_message']}

"""
            prompt += """Provide a helpful hint (not the full solution) that guides the developer toward the solution. 
Keep it concise and educational."""

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful coding coach."},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                max_tokens=200,
                temperature=0.7
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating hint: {str(e)}"

