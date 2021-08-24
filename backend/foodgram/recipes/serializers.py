from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from .models import (
    Ingredient,
    Tag,
    Recipe,
    FavoriteRecipe,
    ShoppingCart,
    IngredientInRecipe,
    Subscribe
)
from users.serializers import CustomUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_ingredients(self, recipe):
        qs = IngredientInRecipe.objects.filter(recipe=recipe)
        return IngredientForRecipeSerializer(qs, many=True).data

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(recipe=recipe, user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=recipe, user=user).exists()


class IngredientForCreateRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientForCreateRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError('Время приготовления должно быть больше 0')
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            ingredient_instance = get_object_or_404(
                Ingredient,
                id=ingredient_id
            )
            ingredient_amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_instance,
                amount=ingredient_amount
            )
        return recipe

    def update(self, instance, validated_data):
        new_tags = validated_data.pop('tags')
        instance.tags.set(new_tags)

        new_ingredients = validated_data.pop('ingredients')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        for new_ingredient in new_ingredients:
            new_ingredient_id = new_ingredient['id']
            ingredient_instance = get_object_or_404(
                Ingredient,
                id=new_ingredient_id
            )
            new_ingredient_amount = new_ingredient['amount']
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient_instance,
                amount=new_ingredient_amount
            )
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance,
            context={
                'request': request
            }
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = (
            'recipe',
            'user'
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {
            'request': request
        }
        return RecipeSerializer(
            instance.recipe,
            context=context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingCart
        fields = (
            'recipe',
            'user'
        )

    def validate(self, attrs):
        user = self.context.get('request').user
        recipe_id = attrs['recipe'].id

        if ShoppingCart.objects.filter(
                user=user,
                recipe__id=recipe_id
        ).exists():
            message = 'Рецепт уже в корзине'
            raise serializers.ValidationError(message)

        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {
            'request': request
        }
        return RecipeForSerializer(
            instance.recipe,
            context=context
        ).data


class RecipeForSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribe',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, author):
        qs = Recipe.objects.filter(author=author)
        return RecipeForSerializer(qs, many=True).data

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_is_subscribe(self, author):
        user = self.context.get('request').user
        return Subscribe.objects.filter(author=user, user=author).exists()


class SubscribeCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscribe
        fields = (
            'user',
            'author')

    def validate(self, attrs):
        user = self.context.get('request').user
        author = attrs['author']

        if user == author:
            message = 'Нельзя подписаться на себя'
            raise serializers.ValidationError(message)
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {
            'request': request
        }
        return SubscribeSerializer(
            instance.author,
            context=context
        ).data
