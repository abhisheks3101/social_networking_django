from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ...models import User
import logging
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)
from django.contrib.auth import authenticate
from ...jwt import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated
from ...custom_response import CustomResponseMixin
logger = logging.getLogger(__name__)


class UserRegistrationView(CustomResponseMixin, APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        data = {
            'token': token,
            'email': user.email,
            'name': user.name
        }
        return self.format_response(
            'User registered successfully',
            data, status_code=status.HTTP_201_CREATED)



class UserLoginView(CustomResponseMixin, APIView):
    def post(self, request, *args, **kwargs):
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
            return self.format_response(
                'User logged in successfully', data)
        else:
            return self.format_response(
                'User Login Failed',
                data = {},
                type ='failure',
                errors={'detail': 'Invalid credentials'},
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            serializer = UserProfileSerializer(request.user)
            return Response({
                    'message': 'User profile fetched successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': 'An unexpected error occurred',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
