from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from recipes.models import Subscribe

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'last_name',
            'first_name',
            'email',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'is_subscribe',
            'email',
            'first_name',
            'last_name',
        )

    def get_is_subscribe(self, following_user):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            author=following_user,
            user=request.user
        ).exists()
