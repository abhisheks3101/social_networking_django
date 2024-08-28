
from social_networking.app_apis.models import User, FriendRequest, Friendship
from django.utils import timezone
from datetime import timedelta
from .custom_response import APIException


def validate_receiver_id(receiver_id, failure_message):
        if not receiver_id:
            raise APIException(message=failure_message, errors="Receiver ID is required")


def get_receiver(receiver_id, sender, failure_message):
    receiver = User.objects.get(id=receiver_id)
    if sender == receiver:
        raise APIException(
            message=failure_message,
            errors="You cannot send a friend request to yourself!",
        )
    return receiver


def check_recent_requests(sender, failure_message):
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    recent_requests = FriendRequest.objects.filter(
        sender=sender, created_at__gte=one_minute_ago
    ).count()
    if recent_requests >= 3:
        raise APIException(
            message=failure_message,
            errors="Cannot send more than 3 friend requests within a minute",
        )


def send_friend_request(sender, receiver, failure_message):
    friend_request, created = FriendRequest.objects.get_or_create(
        sender=sender, receiver=receiver
    )
    if not created:
        raise APIException(
            message=failure_message, errors="Friend request already sent"
        )


def get_friend_request(pk, user, failure_message):
        friend_request = FriendRequest.objects.get(pk=pk)
        if friend_request.receiver != user:
            raise APIException(
                message=failure_message,
                errors="You are not authorized to accept/reject this request",
            )
        return friend_request

def validate_request_status(request_status, failure_message):
    if request_status not in ["accepted", "rejected"]:
        raise APIException(message=failure_message, errors="Invalid Status")
    return request_status


def update_friend_request_status(friend_request, request_status):
    friend_request.status = request_status
    friend_request.save()


def create_friendship(sender, receiver):
    Friendship.objects.create(user1=sender, user2=receiver)