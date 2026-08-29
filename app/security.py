import time
import datetime
import jwt
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User

def get_client_ip(request):
    """
    Safely retrieves the client IP address, handling load balancers and proxies.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # The first IP in the comma-separated list is the original client IP
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip

def generate_jwt_token(user):
    """
    Generates a cryptographically signed JWT token for the given user.
    """
    payload = {
        'user_id': user.id,
        'username': user.username,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24), # Expire in 24 hours
        'iat': datetime.datetime.utcnow(),
    }
    # Uses HS256 algorithm with the secret key loaded from env
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

def decode_jwt_token(token):
    """
    Decodes and validates a JWT token. Returns the payload dict or raises an exception.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])

def check_rate_limit(request, key_prefix="ratelimit"):
    """
    Implements a robust sliding-window rate limiter using Django's cache backend.
    Tracks requests per IP or authenticated user per endpoint.
    
    Returns: (is_limited, quota_details)
    """
    if request.user and request.user.is_authenticated:
        identifier = f"user_{request.user.id}"
    else:
        identifier = f"ip_{get_client_ip(request)}"
        
    # Standardize cache key based on path and identifier
    cache_key = f"{key_prefix}_{identifier}_{request.path}"
    
    limit = getattr(settings, 'RATE_LIMIT_LIMIT', 100)
    window = getattr(settings, 'RATE_LIMIT_WINDOW', 60)
    
    now = time.time()
    
    # Retrieve request timestamps from cache
    history = cache.get(cache_key) or []
    
    # Prune outdated timestamps outside the window
    history = [ts for ts in history if ts > now - window]
    
    if len(history) >= limit:
        # Oldest request in the active window
        oldest_ts = history[0]
        reset_epoch = int(oldest_ts + window)
        retry_after = max(1, int(reset_epoch - now))
        
        return True, {
            'limit': limit,
            'remaining': 0,
            'reset': reset_epoch,
            'retry_after': retry_after
        }
        
    # Append current request timestamp
    history.append(now)
    # Save back to cache with duration of the window
    cache.set(cache_key, history, timeout=window)
    
    reset_epoch = int(now + window)
    return False, {
        'limit': limit,
        'remaining': limit - len(history),
        'reset': reset_epoch,
        'retry_after': 0
    }
