# core/middleware.py or your_app/middleware.py

from datetime import datetime, time
from django.http import HttpResponseForbidden
import logging
from datetime import datetime

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



class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define access hours: 6PM to 9PM
        start_time = time(18, 0)  # 6:00 PM
        end_time = time(21, 0)    # 9:00 PM

        current_time = datetime.now().time()

        # Deny access if current time is NOT between 6PM and 9PM
        if not (start_time <= current_time <= end_time):
            return HttpResponseForbidden("Access to this service is restricted to 6PM - 9PM.")

        response = self.get_response(request)
        return response
