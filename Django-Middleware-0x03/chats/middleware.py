# core/middleware.py or your_app/middleware.py

from datetime import datetime, time
from django.http import HttpResponseForbidden
import logging
from datetime import datetime
from datetime import time
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication


logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('requests.log')
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        return response



# class RestrictAccessByTimeMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Define access hours: 6PM to 9PM
#         start_time = time(18, 0)  # 6:00 PM
#         end_time = time(21, 0)    # 9:00 PM

#         current_time = datetime.now().time()

#         # Deny access if current time is NOT between 6PM and 9PM
#         if not (start_time <= current_time <= end_time):
#             return HttpResponseForbidden("Access to this service is restricted to 6PM - 9PM.")

#         response = self.get_response(request)
#         return response
    




class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to track message counts and timestamps by IP
        # Format: { ip_address: [timestamp1, timestamp2, ...] }
        self.ip_message_times = {}

        # Limit config
        self.MESSAGE_LIMIT = 5
        self.TIME_WINDOW = 60  # seconds (1 minute)

    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/api/conversations/') and '/messages/' in request.path:
            # count and limit messages here
            ip = self.get_client_ip(request)
            now = time.time()

            # Initialize list if first message from this IP
            if ip not in self.ip_message_times:
                self.ip_message_times[ip] = []

            # Remove timestamps older than TIME_WINDOW seconds
            self.ip_message_times[ip] = [t for t in self.ip_message_times[ip] if now - t < self.TIME_WINDOW]

            # Check if user exceeded limit
            if len(self.ip_message_times[ip]) >= self.MESSAGE_LIMIT:
                return JsonResponse({'error': 'Message limit exceeded. Please wait before sending more messages.'}, status=429)

            # Record this message timestamp
            self.ip_message_times[ip].append(now)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        # Try to get IP from X-Forwarded-For if behind proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip






class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request):
        protected_paths = ['/api/conversations/', '/api/messages/']
        if any(request.path.startswith(path) for path in protected_paths):
            # Try to authenticate JWT manually
            try:
                auth_result = self.jwt_authenticator.authenticate(request)
                if auth_result is None:
                    return JsonResponse({'error': 'Authentication required.'}, status=401)
                request.user, _ = auth_result
            except Exception as e:
                return JsonResponse({'error': 'Authentication failed.'}, status=401)
            
            # Check role
            user_role = getattr(request.user, 'role', None)
            if user_role not in ['admin', 'moderator']:
                return JsonResponse({'error': 'Forbidden: insufficient permissions.'}, status=403)

        return self.get_response(request)

