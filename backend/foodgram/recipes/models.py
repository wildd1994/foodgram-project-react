from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def is_hex(value):
    if value[0] != '#' and (len(value[1:]) != 3 or len(value[1:]) != 6):
        raise ValidationError(
            _(f'{value} is not a HEX-color'),
            params={'value': value},
        )


class Ingredient(models.Model):
    name = models.CharField(max_length=200, blank=False)
    measurement_unit = models.CharField(max_length=200)

    REQUIRED_FIELDS = ['name', 'measurement_unit']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(max_length=200, blank=False)
    color = models.CharField(null=True, blank=True, max_length=7, validators=[is_hex])
    slug = models.SlugField(null=True, max_length=200, blank=True)

    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(Ingredient, through='IngredientInRecipe')
    tags = models.ManyToManyField(Tag)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    image = models.ImageField(upload_to='')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.name}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient')
    amount = models.PositiveIntegerField()


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_recipe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_favorited')


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_in_shopping_cart')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_shopping_cart')
