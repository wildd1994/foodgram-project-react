from django.urls import path, include
from rest_framework import routers
from .views import (
    IngredientsViewSet,
    TagsViewSet,
    RecipeViewSet,
    FavoriteRecipeView,
    ShoppingCartView,
    ShoppingCartDownload,
    UserSubscribeListView,
    SubscribeView
)

recipes_api = routers.DefaultRouter()
recipes_api.register('ingredients', IngredientsViewSet, basename='ingredients')
recipes_api.register('tags', TagsViewSet, basename='tags')
recipes_api.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('recipes/download_shopping_cart/',
         ShoppingCartDownload.as_view(),
         name='download_shopping_cart'
         ),
    path('', include(recipes_api.urls)),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteRecipeView.as_view(),
         name='favorite_recipe'
         ),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartView.as_view(),
         name='shopping_cart'
         ),
    path('users/subscriptions/',
         UserSubscribeListView.as_view(),
         name='subscriptions'
         ),
    path('users/<int:author_id>/subscribe/',
         SubscribeView.as_view(),
         name='create_destroy_subs'
         ),
]
