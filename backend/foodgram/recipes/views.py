from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from .models import Ingredient, Tag, Recipe, FavoriteRecipe, ShoppingCart, IngredientInRecipe
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer, FavoriteSerializer, ShoppingCartSerializer, CreateRecipeSerializer
from rest_framework import permissions, views
from .permissions import IsAuthor
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CustomFilter


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
            queryset = Ingredient.objects.filter(name__startswith=ingredient_name.lower())
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

    def get_permissions(self):
        if self.action in ['put', 'delete']:
            self.permission_classes = [IsAuthor()]
            return self.permission_classes
        if self.action == 'post':
            self.permission_classes = [permissions.IsAuthenticated()]
            return self.permission_classes
        self.permission_classes = [permissions.AllowAny()]
        return self.permission_classes

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
        shopping_cart = request.user.user_shopping_cart.all()
        buying_list = dict()
        for item in shopping_cart:
            ingredients = IngredientInRecipe.objects.filter(recipe=item.recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit

                if name not in buying_list:
                    buying_list[name] = {
                        'Еденица измерения': measurement_unit,
                        'Количество': amount
                    }
                else:
                    buying_list[name]['Количество'] = buying_list[name]['Количество']+amount

        wishlist = []
        for item in buying_list:
            wishlist.append(f'{item} - {buying_list[item]["Количество"]} '
                            f'{buying_list[item]["Еденица измерения"]} \n')

        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response


