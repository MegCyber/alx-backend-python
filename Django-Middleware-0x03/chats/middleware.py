import logging
from datetime import datetime, time
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from collections import defaultdict
from threading import Lock
import time as time_module

# Configure logging for request logging
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

# Create file handler for logging requests
file_handler = logging.FileHandler('requests.log')
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
if not logger.handlers:
    logger.addHandler(file_handler)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs each user's requests to a file,
    including the timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get user information
        user = request.user if request.user.is_authenticated else 'Anonymous'
        
        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Continue processing the request
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware that restricts access to the messaging app
    during certain hours of the day (outside 9 AM to 6 PM).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get current time
        current_time = datetime.now().time()
        
        # Define allowed time range (9 AM to 6 PM)
        start_time = time(9, 0)  # 9:00 AM
        end_time = time(18, 0)   # 6:00 PM
        
        # Check if current time is outside allowed range
        if not (start_time <= current_time <= end_time):
            return JsonResponse(
                {
                    'error': 'Access denied',
                    'message': 'The messaging app is only accessible between 9 AM and 6 PM.',
                    'current_time': current_time.strftime('%H:%M:%S')
                },
                status=403
            )
        
        # Continue processing the request
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware that limits the number of chat messages a user can send
    within a certain time window (rate limiting based on IP address).
    Limits to 5 messages per minute per IP address.
    """
    
    # Class-level storage for tracking requests
    request_counts = defaultdict(list)
    lock = Lock()
    
    # Configuration
    MAX_REQUESTS = 5
    TIME_WINDOW = 60  # seconds (1 minute)
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Only apply rate limiting to POST requests (message sending)
        if request.method == 'POST' and '/api/messages' in request.path:
            # Get client IP address
            ip_address = self.get_client_ip(request)
            
            current_time = time_module.time()
            
            with self.lock:
                # Get request history for this IP
                request_times = self.request_counts[ip_address]
                
                # Remove requests outside the time window
                request_times = [
                    req_time for req_time in request_times 
                    if current_time - req_time < self.TIME_WINDOW
                ]
                
                # Check if limit exceeded
                if len(request_times) >= self.MAX_REQUESTS:
                    return JsonResponse(
                        {
                            'error': 'Rate limit exceeded',
                            'message': f'You can only send {self.MAX_REQUESTS} messages per minute. Please try again later.',
                            'retry_after': int(self.TIME_WINDOW - (current_time - request_times[0]))
                        },
                        status=429  # Too Many Requests
                    )
                
                # Add current request time
                request_times.append(current_time)
                self.request_counts[ip_address] = request_times
        
        # Continue processing the request
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Extract the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolePermissionMiddleware(MiddlewareMixin):
    """
    Middleware that checks the user's role before allowing access
    to specific actions. Only admin or moderator roles are allowed.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Define protected paths that require admin/moderator access
        protected_paths = [
            '/api/users/',
            '/api/conversations/',
            '/admin/',
        ]
        
        # Check if the request path requires role-based permission
        requires_permission = any(
            request.path.startswith(path) for path in protected_paths
        )
        
        if requires_permission:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        'error': 'Authentication required',
                        'message': 'You must be logged in to access this resource.'
                    },
                    status=401
                )
            
            # Check user role
            user_role = getattr(request.user, 'role', None)
            
            # Allow access only for admin or moderator
            # Also allow Django superusers
            if user_role not in ['admin', 'moderator'] and not request.user.is_superuser:
                return JsonResponse(
                    {
                        'error': 'Permission denied',
                        'message': 'You must be an admin or moderator to access this resource.',
                        'your_role': user_role or 'unknown'
                    },
                    status=403
                )
        
        # Continue processing the request
        response = self.get_response(request)
        return response
    
class RolePermissionMiddleware(MiddlewareMixin):
    pass

# Optional: Additional utility middleware for offensive language detection
class OffensiveLanguageDetectionMiddleware(MiddlewareMixin):
    """
    Optional middleware to detect and block offensive language in messages.
    This checks the content of POST requests for offensive words.
    """
    
    # List of offensive words to block (add more as needed)
    OFFENSIVE_WORDS = [
        'offensive1', 'offensive2', 'badword1', 'badword2',
        # Add actual offensive words here
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Check POST requests for messages
        if request.method == 'POST' and '/api/messages' in request.path:
            try:
                # Get message body from request
                import json
                if request.body:
                    body = json.loads(request.body)
                    message_body = body.get('message_body', '').lower()
                    
                    # Check for offensive language
                    for word in self.OFFENSIVE_WORDS:
                        if word in message_body:
                            return JsonResponse(
                                {
                                    'error': 'Offensive language detected',
                                    'message': 'Your message contains inappropriate content and cannot be sent.'
                                },
                                status=400
                            )
            except Exception:
                pass
        
        response = self.get_response(request)
        return response