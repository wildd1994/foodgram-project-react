from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import (
    mixins,
    viewsets,
    status,
    generics,
    pagination
)
from rest_framework.response import Response
from .models import (
    Ingredient,
    Tag,
    Recipe,
    FavoriteRecipe,
    ShoppingCart,
    Subscribe
)
from .serializers import (
    IngredientSerializer,
    TagSerializer, RecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    CreateRecipeSerializer,
    SubscribeSerializer,
    SubscribeCreateSerializer
)
from rest_framework import permissions, views
from .permissions import RecipePermissions
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CustomFilter

User = get_user_model()


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class ListCreateRetrieveUpdateDestroy(mixins.ListModelMixin,
                                      mixins.CreateModelMixin,
                                      mixins.RetrieveModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin,
                                      viewsets.GenericViewSet):
    pass


class IngredientsViewSet(ListRetrieveViewSet):

    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        ingredient_name = self.request.query_params.get('name')
        if ingredient_name is not None:
            queryset = Ingredient.objects.filter(
                name__startswith=ingredient_name.lower()
            )
        return queryset


class TagsViewSet(ListRetrieveViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class RecipeViewSet(ListCreateRetrieveUpdateDestroy):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomFilter
    permission_classes = [RecipePermissions]

    def get_serializer_class(self):
        if 'list' in self.action or 'retrieve' in self.action:
            return RecipeSerializer
        return CreateRecipeSerializer


class FavoriteRecipeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id
        }
        serializer = FavoriteSerializer(
            data=data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite = FavoriteRecipe.objects.filter(recipe=recipe, user=user)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Этого рецепта нет в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ShoppingCartView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id
        }
        serializer = ShoppingCartSerializer(
            data=data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Этого рецепта нет в корзине'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ShoppingCartDownload(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ingredients = request.user.user_shopping_cart.select_related(
            'recipe'
        ).order_by(
            'recipe__ingredients__name'
        ).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(
            amount=Sum('recipe__recipe__amount')
        ).all()

        wishlist = []
        for ingredient in ingredients:
            wishlist.append(
                f'{ingredient["recipe__ingredients__name"]}'
                f' - {ingredient["amount"]}'
                f' {ingredient["recipe__ingredients__measurement_unit"]}'
                f'\n')

        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response


class UserSubscribeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscribeSerializer
    http_method_names = ['get']
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        follower = self.request.user
        return User.objects.filter(following__user=follower)


class SubscribeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, author_id):
        user = request.user.id
        data = {
            'user': user,
            'author': author_id
        }
        serializer = SubscribeCreateSerializer(
            data=data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, pk=author_id)
        follow = Subscribe.objects.filter(author=author, user=user)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )
