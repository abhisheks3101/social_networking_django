from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from .serializers import User
from .serializers import UserSerializer
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from social_networking.app_apis.models import User, FriendRequest, Friendship
from rest_framework.views import APIView
from ...custom_response import CustomResponseMixin, APIException
from django.db import transaction
import logging
from ...utils import *
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10


class UserSearchView(generics.ListAPIView):
    """
    API to search for different users on the base of name and email
    response: {
            "message": "User Fetched Successfully",
            "data": {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "id": "7e7b4229-cc29-46ca-a01f-093b0c439a80",
                        "email": "abhi@gmail.com",
                        "name": "Abhishek"
                    }
                ]
            }
        }
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["email", "name"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_keyword = self.request.query_params.get("search", None)
        if search_keyword:
            queryset = queryset.filter(
                Q(email__iexact=search_keyword) | Q(name__icontains=search_keyword)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(
                    serializer.data).data
                return Response(
                    {
                        "message": "User Fetched Successfully",
                        "data": {
                            "count": paginated_response["count"],
                            "next": paginated_response["next"],
                            "previous": paginated_response["previous"],
                            "results": paginated_response["results"],
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"User search successful for keyword " \
                "{request.query_params.get('search')}' by user '{request.user.email}'")
            return Response(
                {"message": "User Fetched Successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error during user search: {str(e)}")
            return Response(
                {"message": "An unexpected error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FriendRequestView(CustomResponseMixin, APIView):
    """
    Handle sending, accepting, and rejecting friend requests.

    POST:
    Send a friend request from the authenticated user to another user.
    Requires 'receiver_id' in the request data to specify the recipient's user ID.
    Limits to sending a maximum of 3 friend requests within a minute.

    PUT:
    Accept or reject a friend request.
    Requires the 'pk' parameter in the URL to specify the friend request ID.
    The request body must contain 'status' with values 'accepted' or 'rejected'.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        failure_message = "Failed to send friend request"

        sender = request.user
        receiver_id = request.data.get("receiver_id")

        # validations
        validate_receiver_id(receiver_id, failure_message)
        check_recent_requests(sender, failure_message)
        receiver = get_receiver(receiver_id, sender, failure_message)

        try:
            with transaction.atomic():
                # Send the friend request
                friend_request, created = FriendRequest.objects.get_or_create(
                    sender=sender, receiver=receiver
                )
                if not created:
                    raise APIException(
                        message=failure_message,
                        errors="Friend request already sent"
                    )
                return self.format_response(
                    message="Friend request sent",
                    status_code=status.HTTP_201_CREATED
                )
        except APIException as e:
            transaction.set_rollback(True)
            raise e
        except Exception as e:
            transaction.set_rollback(True)
            raise APIException(message="An unexpected error occurred", errors=str(e))


    def put(self, request, pk):
        failure_message = "Failed to accept/reject friend request"

        friend_request = get_friend_request(
            pk,
            request.user,
            failure_message
        )
        request_status = validate_request_status(
            request.data.get("status"),
            failure_message)

        try:
            with transaction.atomic():
                update_friend_request_status(friend_request, request_status)

                if request_status == "accepted":
                    create_friendship(
                        friend_request.sender, friend_request.receiver)

                return self.format_response(
                    message=f"Friend request {request_status}",
                    status_code=status.HTTP_200_OK,
                )
        except APIException as e:
            transaction.set_rollback(True)
            raise e
        except Exception as e:
            transaction.set_rollback(True)
            raise APIException(message="An unexpected error occurred", errors=str(e))


class FriendListView(generics.ListAPIView):
    """
    API endpoint to fetch friends list.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        friends = Friendship.objects.filter(Q(user1=user) | Q(user2=user))
        friend_ids = [
            friend.user1.id if friend.user1 != user else friend.user2.id
            for friend in friends
        ]
        return User.objects.filter(id__in=friend_ids)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data).data
                return Response(
                    {
                        "message": "User Friends List Fetched Successfully",
                        "data": {
                            "count": paginated_response["count"],
                            "next": paginated_response["next"],
                            "previous": paginated_response["previous"],
                            "results": paginated_response["results"],
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {"message": "User Fetched Successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error fetching user friends list: {str(e)}")
            return Response(
                {"message": "An unexpected error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PendingFriendRequestView(CustomResponseMixin, APIView):
    """
    API endpoint to fetch pending friend requests.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        try:
            user = self.request.user
            friend_requests_obj = (
                FriendRequest.objects.select_related("sender")
                .filter(receiver=user, status="pending")
                .values("id", "sender__name", "sender__email")
            )
            sender_details = []
            for item in friend_requests_obj:
                sender_data = {
                    "friend_request_id": item["id"],
                    "name": item["sender__name"],
                    "email": item["sender__email"],
                }
                sender_details.append(sender_data)
            return self.format_response(
                message="Pending friend requests fetched successfully",
                data=sender_details,
                type="success",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error fetching pending friend requests: {str(e)}")
            raise APIException(message="An unexpected error occurred", errors=str(e))