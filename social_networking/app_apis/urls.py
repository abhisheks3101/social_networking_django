from django.urls import path
from  .v1.user_auth.views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
)
from .v1.networking_application.views import (
    UserSearchView,
    FriendRequestView,
    FriendRequestView,
    PendingFriendRequestView,
    FriendListView
)

urlpatterns = [
    path('user/register/',
        UserRegistrationView.as_view(),
        name='user-register'
    ),
    path('user/login/',
        UserLoginView.as_view(),
        name='user-login'
    ),
    path('user/detail/',
        UserProfileView.as_view(),
        name='user-detail'
    ),
    path('user/search/',
        UserSearchView.as_view(),
        name='user-search'
    ),
    path('user/friend-requests/',
        FriendRequestView.as_view(),
        name='send-friend-request'
    ),
    path('user/friend-request/<uuid:pk>/',
        FriendRequestView.as_view(),
        name='respond-friend-request'
    ),
    path('user/friend-requests-pending/',
        PendingFriendRequestView.as_view(),
        name='pending-friend-requests'),
    path('user/friends-list/',
        FriendListView.as_view(),
        name='user-friends-list'),
]
