from django_filters import rest_framework as filters
from .models import Recipe, Tag


class CustomFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(
        method='get_favorite'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags',
                  'author',
                  'is_favorited',
                  'is_in_shopping_cart'
                  )

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(
                favorited_recipe__user=self.request.user
            )
        return queryset.exclude(
            favorited_recipe__user=self.request.user
        )

    def get_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                recipe_in_shopping_cart__user=self.request.user
            )
        return queryset.exclude(
            recipe_in_shopping_cart__user=self.request.user
        )
