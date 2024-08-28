from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import exception_handler


class APIException(Exception):
    """
    Custom exception class to handle API exceptions.
    """
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super().__init__(self.message)


class CustomResponseMixin:
    """
    Custom response mixin to handle exceptions and format responses.
    """
    def handle_exception(self, exc):
        # Handle custom API exceptions
        if isinstance(exc, APIException):
            return self.format_response(
                exc.message,
                errors={'detail':exc.errors},
                status_code=status.HTTP_400_BAD_REQUEST,
                type="failure"
            )
        # Handle validation errors
        elif isinstance(exc, ValidationError):
            return Response({
                'message': f'{self.get_view_name()} Failed',
                'data': {},
                'type': 'failure',
                'errors': exc.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        # Handle other exceptions
        else:
            response = exception_handler(exc, self.request)
            if response is None:
                return self.format_response(
                    'An unexpected error occurred',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    type="error"
                )
            return response

    def format_response(
            self,
            message,
            data=None,
            type="success",
            status_code=status.HTTP_200_OK,
            errors =None):
        return Response({
            'message': message,
            'data': data or {},
            'type': type,
            'errors': errors
        }, status=status_code)


def custom_exception_handler(exc, context):
    """
    Custom exception for 401 error when token gets expired
    """
    response = exception_handler(exc, context)
    if response is not None and response.status_code == 401:
        return Response({
            'message': 'Unauthorized',
            'data': {},
            'type': 'failure',
            'errors': {
                'detail': 'Token Expired or Invalid'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)
    return response
