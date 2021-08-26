from django.contrib import admin
from .models import (
    Ingredient,
    Tag,
    IngredientInRecipe,
    Recipe,
    FavoriteRecipe,
    Subscribe
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']


class MembershipInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [MembershipInline]
    list_display = ['author', 'name']
    list_filter = ('name', 'author', 'tags')


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user']


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['author', 'user']


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'amount']
    list_filter = ('recipe', 'ingredient')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
