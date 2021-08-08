from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from recipes.models import Subscribe

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            'id',
            'username',
            'password',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            'id',
            'username',
            'is_subscribe',
            'email',
        )

    def get_is_subscribe(self, obj):
        request = self.context.get('request')
        user = obj
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(author=request.user, user=user).exists()
