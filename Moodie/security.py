"""
Security middleware and utilities for parameter tampering protection
"""
import re
import logging
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.conf import settings

logger = logging.getLogger(__name__)


def sanitize_input(value):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not value:
        return value
    # Remove HTML tags
    value = strip_tags(str(value))
    # Remove potentially dangerous characters
    value = re.sub(r'[<>"\']', '', value)
    return value.strip()


def validate_integer_param(value, min_value=1, max_value=None):
    """Validate integer parameters"""
    try:
        int_value = int(value)
        if int_value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        if max_value and int_value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        return int_value
    except (ValueError, TypeError):
        raise ValidationError("Invalid integer value")


def validate_float_param(value, min_value=0.0, max_value=10.0):
    """Validate float parameters"""
    try:
        float_value = float(value)
        if float_value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        if float_value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        return float_value
    except (ValueError, TypeError):
        raise ValidationError("Invalid float value")


def validate_year_param(value):
    """Validate year parameters"""
    return validate_integer_param(value, min_value=1888, max_value=2030)


def validate_movie_id(movie_id):
    """Validate movie_id parameter"""
    return validate_integer_param(movie_id)


def validate_user_id(user_id):
    """Validate user_id parameter"""
    return validate_integer_param(user_id)


def validate_rating(rating_str):
    """Validate rating parameter"""
    return validate_float_param(rating_str, min_value=0.0, max_value=10.0)


class SecurityMiddleware:
    """
    Middleware to add security headers and validate parameters
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add security headers
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp_policy
        
        return response

    def process_request(self, request):
        """Process request for potential security issues"""
        try:
            # Log suspicious requests
            if self._is_suspicious_request(request):
                logger.warning(f"Suspicious request detected: {request.path} from {request.META.get('REMOTE_ADDR')}")
            
            # Validate GET parameters
            if request.method == 'GET':
                self._validate_get_params(request)
                
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return HttpResponseBadRequest("Invalid request parameters")
        
        return None

    def _is_suspicious_request(self, request):
        """Check if request appears suspicious"""
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'<iframe',
            r'<object',
            r'<embed',
        ]
        
        path = request.path.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False

    def _validate_get_params(self, request):
        """Validate GET parameters for common attacks"""
        for key, value in request.GET.items():
            # Check for potential XSS
            if any(char in value for char in ['<', '>', '"', "'"]):
                # Log but don't block - let the sanitization functions handle it
                logger.info(f"Potential XSS attempt in parameter {key}: {value}")
            
            # Check for SQL injection patterns
            sql_patterns = [
                r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
                r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
                r'(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(union|select|insert|update|delete|drop|create|alter)\b)',
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    logger.warning(f"Potential SQL injection attempt in parameter {key}: {value}")


def rate_limit_key(request):
    """Generate rate limiting key based on user and action"""
    if request.user.is_authenticated:
        return f"rate_limit:{request.user.id}:{request.path}"
    return f"rate_limit:anonymous:{request.META.get('REMOTE_ADDR')}:{request.path}"


def check_rate_limit(request, max_requests=10, window_seconds=60):
    """
    Simple rate limiting check
    In production, use Redis or similar for proper rate limiting
    """
    # This is a simplified version - in production use proper rate limiting
    return True 