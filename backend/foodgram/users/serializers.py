from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import authenticate, get_user_model
from .models import Follow
from rest_framework import serializers
from recipes.models import Recipe

User = get_user_model()


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label='Email')
    password = serializers.CharField(
        label=('Password',),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            if not user:
                message = 'Введите корректные данные'
                raise serializers.ValidationError(message, code='authorization')
        if not email:
            message = 'Введите email'
            raise serializers.ValidationError(message, code='authorization')
        if not password:
            message = 'Введите пароль'
            raise serializers.ValidationError(message, code='authorization')

        attrs['user'] = user
        return attrs


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
        return Follow.objects.filter(author=request.user, user=user).exists()


class RecipeForSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'cooking_time', 'image']


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'is_subscribe', 'recipes', 'recipes_count']

    def get_recipes(self, obj):
        author = obj
        qs = Recipe.objects.filter(author=author)
        return RecipeForSerializer(qs, many=True).data

    def get_recipes_count(self, obj):
        author = obj
        count = Recipe.objects.filter(author=author).count()
        return count

    def get_is_subscribe(self, obj):
        author = obj
        user = self.context.get('request').user
        if Follow.objects.filter(author=user, user=author).exists():
            return True
        return False


class FollowCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ['user', 'author']

    def validate(self, attrs):
        user = self.context.get('request').user
        author = attrs['author']

        if Follow.objects.filter(user=user, author=author).exists():
            message = 'Подписка уже оформлена'
            raise serializers.ValidationError(message)
        if user == author:
            message = 'Нельзя подписаться на себя'
            raise serializers.ValidationError(message)
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {
            'request': request
        }
        return FollowSerializer(
            instance.author,
            context=context
        ).data
