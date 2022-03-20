from django.urls import path

from .views import (
    FriendShipCreateTestView, FriendShipTestAttemptView
)

urlpatterns = [
    path('create-test/', FriendShipCreateTestView.as_view(), name='create-test'),
    path('attempt-test/<test_uuid>/', FriendShipTestAttemptView.as_view(), name='attempt-test')
]
