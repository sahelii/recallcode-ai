"""
Services for problem-related operations including code execution.
"""
import requests
from django.conf import settings
from typing import Optional, Dict, Any


class Judge0Service:
    """Service for executing code using Judge0 API."""
    
    @staticmethod
    def execute_code(
        code: str,
        language: str,
        stdin: Optional[str] = None,
        expected_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute code using Judge0 API.
        
        Args:
            code: Source code to execute
            language: Programming language (python, javascript, java, cpp, c, go, rust)
            stdin: Standard input (optional)
            expected_output: Expected output for validation (optional)
        
        Returns:
            Dict with execution results
        """
        # Map language names to Judge0 language IDs
        language_map = {
            'python': 92,  # Python 3
            'javascript': 93,  # Node.js
            'java': 91,  # Java
            'cpp': 54,  # C++17
            'c': 50,  # C
            'go': 60,  # Go
            'rust': 73,  # Rust
        }
        
        language_id = language_map.get(language.lower(), 92)  # Default to Python
        
        # Judge0 API endpoint
        api_url = f"{settings.JUDGE0_API_URL}/submissions"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        if settings.JUDGE0_API_KEY:
            headers['X-RapidAPI-Key'] = settings.JUDGE0_API_KEY
            headers['X-RapidAPI-Host'] = 'judge0-ce.p.rapidapi.com'
        
        payload = {
            'source_code': code,
            'language_id': language_id,
            'stdin': stdin or '',
        }
        
        try:
            # Submit code
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 201:
                return {
                    'success': False,
                    'error': f'Judge0 API error: {response.status_code}',
                    'message': response.text
                }
            
            submission_token = response.json().get('token')
            
            # Poll for results
            result_url = f"{settings.JUDGE0_API_URL}/submissions/{submission_token}"
            import time
            
            for _ in range(10):  # Poll up to 10 times
                time.sleep(1)
                result_response = requests.get(result_url, headers=headers, timeout=5)
                
                if result_response.status_code == 200:
                    result = result_response.json()
                    
                    # Check if compilation/execution is complete
                    status_id = result.get('status', {}).get('id')
                    
                    if status_id in [1, 2]:  # In Queue or Processing
                        continue
                    
                    # Execution complete
                    return Judge0Service._format_result(result, expected_output)
            
            return {
                'success': False,
                'error': 'Execution timeout',
                'message': 'Code execution took too long'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Execution error',
                'message': str(e)
            }
    
    @staticmethod
    def _format_result(result: Dict, expected_output: Optional[str] = None) -> Dict[str, Any]:
        """Format Judge0 result into our standard format."""
        status_id = result.get('status', {}).get('id')
        status_description = result.get('status', {}).get('description', 'Unknown')
        
        # Status IDs: 3=Accepted, 4=Wrong Answer, 5=Time Limit, 6=Compilation Error, etc.
        is_accepted = status_id == 3
        is_compilation_error = status_id == 6
        is_runtime_error = status_id in [7, 8, 9, 10, 11, 12]
        
        output = {
            'success': is_accepted,
            'is_accepted': is_accepted,
            'status': status_description,
            'status_id': status_id,
            'stdout': result.get('stdout', ''),
            'stderr': result.get('stderr', ''),
            'compile_output': result.get('compile_output', ''),
            'runtime': result.get('time', 0) * 1000,  # Convert to milliseconds
            'memory': result.get('memory', 0),  # Already in KB
            'message': status_description,
        }
        
        if is_compilation_error:
            output['error_message'] = result.get('compile_output', 'Compilation error')
        elif is_runtime_error:
            output['error_message'] = result.get('stderr', 'Runtime error')
        elif not is_accepted:
            output['error_message'] = status_description
        
        # Validate against expected output if provided
        if expected_output and is_accepted:
            actual_output = output['stdout'].strip()
            expected = expected_output.strip()
            if actual_output != expected:
                output['success'] = False
                output['is_accepted'] = False
                output['error_message'] = f'Expected: {expected}, Got: {actual_output}'
        
        return output
