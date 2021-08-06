from django.urls import path, include
from .views import UserFollowListView, Subscribe, UserAuthToken, UserDeleteToken


urlpatterns = [
    path('users/subscriptions/', UserFollowListView.as_view(), name='subscriptions'),
    path('users/<int:author_id>/subscribe/', Subscribe.as_view(), name='create_destroy_subs'),
    path('', include('djoser.urls')),
    path('auth/token/login/', UserAuthToken.as_view()),
    path('auth/token/logout/', UserDeleteToken.as_view()),
]
