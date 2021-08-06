from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from .models import Ingredient, Tag, Recipe, FavoriteRecipe, ShoppingCart, IngredientInRecipe
from users.serializers import CustomUserSerializer, RecipeForSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

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
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        qs = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientForRecipeSerializer(qs, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        recipe = obj
        return FavoriteRecipe.objects.filter(recipe=recipe, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        recipe = obj
        return ShoppingCart.objects.filter(recipe=recipe, user=user).exists()


class IngredientForCreateRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientForCreateRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            ingredient_instance = Ingredient.objects.get(id=ingredient_id)
            ingredient_amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_instance,
                amount=ingredient_amount
            )
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get('tags') is not None:
            new_tags = validated_data.pop('tags')
            old_tags = instance.tags.all()

            for tag in old_tags:
                instance.tags.remove(tag)

            for tag in new_tags:
                instance.tags.add(tag)

        if validated_data.get('ingredients') is not None:
            new_ingredients = validated_data.pop('ingredients')
            old_ingredients = instance.ingredients.all()

            for ingredient in old_ingredients:
                instance.ingredients.remove(ingredient)

            for new_ingredient in new_ingredients:
                new_ingredient_id = new_ingredient['id']
                ingredient_instance = Ingredient.objects.get(id=new_ingredient_id)
                new_ingredient_amount = new_ingredient['amount']
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient_instance,
                    amount=new_ingredient_amount
                )
            recipe = Recipe.objects.filter(id=instance.id)
            recipe.update(**validated_data)
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
        fields = ['recipe', 'user']

    def validate(self, attrs):
        user = self.context.get('request').user
        recipe_id = attrs['recipe'].id

        if FavoriteRecipe.objects.filter(user=user, recipe__id=recipe_id).exists():
            message = 'Рецепт был добавлен ранее'
            raise serializers.ValidationError(message)

        return attrs

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
        fields = ['recipe', 'user']

    def validate(self, attrs):
        user = self.context.get('request').user
        recipe_id = attrs['recipe'].id

        if ShoppingCart.objects.filter(user=user, recipe__id=recipe_id).exists():
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

