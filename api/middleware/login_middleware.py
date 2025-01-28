from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.deprecation import MiddlewareMixin
import loguru
import json

class APIRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        '''Log the incoming request method and path'''
        loguru.logger.info(f"Incoming request: {request.method} {request.path}")

        '''Handle JSON request body'''
        if request.content_type == 'application/json':
            try:
                ''' Try parsing the request body (useful for validating incoming JSON data)'''
                request.data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"message": "Malformed JSON in request body"}, status=400)

        ''' Check if JWT authentication is required (e.g., if the request has an Authorization header)'''
        if request.path.startswith('/api/'):  # Apply to all API paths (you can customize this)
            authorization_header = request.headers.get('Authorization', None)
            if authorization_header:
                if authorization_header.startswith('Bearer '):
                    token = authorization_header.split(' ')[1]  # Extract the token
                    authentication = JWTAuthentication()
                    try:
                        '''Validate the token and get the user'''
                        user = authentication.get_validated_token(token)
                        request.user = user
                    except Exception as e:
                        loguru.logger.error(f"JWT Authentication failed: {str(e)}")
                        return JsonResponse({"message": "Invalid or expired token"}, status=401)
                else:
                    return JsonResponse({"message": "Authorization token must start with 'Bearer'"}, status=400)

        return None

    def process_response(self, request, response):
        """
        This function is called after the view has been called and before the response
        is returned to the client.
        """
        # Log the response status code
        loguru.logger.info(f"Response status: {response.status_code} for {request.method} {request.path}")
        
        # You can add CORS headers if needed for APIs that are accessed from a frontend
        response['Access-Control-Allow-Origin'] = '*'  # Adjust according to your CORS policy
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
