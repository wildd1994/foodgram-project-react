from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def is_hex(value):
    if value[0] != '#' and (len(value) != 4 or len(value) != 7):
        raise ValidationError(
            _(f'{value} is not a HEX-color'),
            params={'value': value},
        )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Еденица измерения'
    )

    class Meta:
        verbose_name = 'Интгредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_list'
            ),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название тега'
    )
    color = models.CharField(
        null=True,
        blank=True,
        max_length=7,
        validators=[is_hex],
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        null=True,
        max_length=200,
        blank=True,
        verbose_name='Уникальный слаг'
    )

    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Теги для рецепта'
    )
    text = models.TextField(
        verbose_name='Способ приготовления'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )
    image = models.ImageField(
        upload_to='',
        verbose_name='Изображение'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента'
    )


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_recipe',
        verbose_name='Избранный рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_favorited',
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_list'
            ),
        ]
        verbose_name = 'Избранное'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_shopping_cart',
        verbose_name='Рецепт в корзине'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart_list'
            ),
        ]
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe_list'
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
