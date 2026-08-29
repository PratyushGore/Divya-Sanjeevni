import logging
import jwt
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from .security import decode_jwt_token, check_rate_limit, get_client_ip

logger = logging.getLogger('security')

class JWTAuthenticationMiddleware:
    """
    Middleware to handle JWT authentication via Authorization Bearer token.
    Validates tokens on every request and assigns request.user if valid.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = decode_jwt_token(token)
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                if user.is_active:
                    request.user = user
                    # Flag to track token-based auth
                    request.jwt_authenticated = True
                else:
                    logger.warning(
                        f"AUTH_FAILURE: Attempted login by inactive user ID {user_id} "
                        f"from IP {get_client_ip(request)}."
                    )
                    return JsonResponse({'status': 'error', 'message': 'User account is disabled.'}, status=401)
            except jwt.ExpiredSignatureError:
                logger.warning(f"AUTH_FAILURE: Expired JWT token presented from IP {get_client_ip(request)}.")
                return JsonResponse({'status': 'error', 'message': 'Token has expired.'}, status=401)
            except (jwt.InvalidTokenError, User.DoesNotExist) as e:
                logger.warning(f"AUTH_FAILURE: Invalid JWT token ({str(e)}) presented from IP {get_client_ip(request)}.")
                return JsonResponse({'status': 'error', 'message': 'Invalid token.'}, status=401)
                
        return self.get_response(request)


class RateLimitMiddleware:
    """
    Middleware to apply IP-based and user-based rate limits on all public and admin API routes.
    Injects remaining quota and reset metadata in response headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only apply API rate limiting to paths under /api/
        if request.path.startswith('/api/'):
            is_limited, quota = check_rate_limit(request)
            
            if is_limited:
                logger.warning(
                    f"RATE_LIMIT_EXCEEDED: IP/User from {get_client_ip(request)} "
                    f"hit rate limit on endpoint '{request.path}'."
                )
                response = JsonResponse({
                    'status': 'error',
                    'message': 'Too Many Requests. Rate limit exceeded.'
                }, status=429)
                
                # Injects standard headers for retry window
                response['X-RateLimit-Limit'] = str(quota['limit'])
                response['X-RateLimit-Remaining'] = str(quota['remaining'])
                response['X-RateLimit-Reset'] = str(quota['reset'])
                response['Retry-After'] = str(quota['retry_after'])
                return response
                
            # If not limited, allow downstream processing
            response = self.get_response(request)
            
            # Append headers indicating remaining quota
            response['X-RateLimit-Limit'] = str(quota['limit'])
            response['X-RateLimit-Remaining'] = str(quota['remaining'])
            response['X-RateLimit-Reset'] = str(quota['reset'])
            return response
            
        return self.get_response(request)


class SecurityHeadersMiddleware:
    """
    Middleware to inject custom secure HTTP headers (equivalent to Helmet.js).
    Protects against XSS, clickjacking, MIME sniffing, and downgrade attacks.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # 1. Content Security Policy (CSP)
        # Allows self resources, unpkg.com for Lucide icons, and google fonts/styles
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://unpkg.com 'unsafe-inline'; "
            "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "frame-src 'self'; "
            "object-src 'none'; "
            "connect-src 'self';"
        )
        
        # 2. Referrer Policy
        response['Referrer-Policy'] = 'same-origin'
        
        # 3. Permissions Policy (Disables browser hardware permissions by default)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
