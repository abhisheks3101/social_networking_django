from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView
import logging
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)
from django.contrib.auth import authenticate
from ...jwt import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated
from ...custom_response import CustomResponseMixin, APIException

logger = logging.getLogger(__name__)


class UserRegistrationView(CustomResponseMixin, APIView):
    """
    API endpoint for user registration.

    POST:
    Register a new user with the provided details.
    Requires 'email', 'password', and optionally 'name'.
    Returns a token for authentication in subsequent requests.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.
        """
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token = get_tokens_for_user(user)
            data = {
                'token': token,
                'email': user.email,
                'name': user.name
            }
            logger.info(f"User registered successfully: {user.email}")
            return self.format_response(
                'User registered successfully',
                data, status_code=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return self.format_response(
                'Failed to register user',
                data={}, type='failure',
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            return self.format_response(
                'Failed to register user',
                data={}, type='failure',
                errors={'detail': 'Failed to register user'},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class UserLoginView(CustomResponseMixin, APIView):
    """
    API endpoint for user login.

    POST:
    Log in a user with email and password.
    Returns a token for authentication in subsequent requests.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user login.
        """
        try:
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.data.get('email').lower()
            password = serializer.data.get('password')

            user = authenticate(email=email, password=password)
            if user:
                token = get_tokens_for_user(user)
                data = {
                    'token': token,
                    'email': user.email,
                }
                logger.info(f"User logged in successfully: {user.email}")
                return self.format_response(
                    'User logged in successfully', data)
            else:
                return self.format_response(
                    'User Login Failed',
                    data={},
                    type='failure',
                    errors={'detail': 'Invalid credentials'},
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            logger.error(f"User login failed: {str(e)}")
            return self.format_response(
                'Failed to log in user',
                data={}, type='failure',
                errors={'detail': 'Failed to log in user'},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    """
    API endpoint to retrieve logged-in user details.

    GET:
    Fetch details of the logged-in user.
    Requires authentication token in headers.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to fetch user profile.
        """
        try:
            serializer = UserProfileSerializer(request.user)
            logger.info(f"User profile fetched successfully: {request.user.email}")
            return Response({
                'message': 'User profile fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to fetch user profile: {str(e)}")
            return Response({
                'message': 'An unexpected error occurred',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)