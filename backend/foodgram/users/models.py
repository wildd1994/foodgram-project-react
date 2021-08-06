from django.db import models
from django.contrib.auth.models import AbstractUser


class FoodgramUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('id',)


class Follow(models.Model):
    user = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique_list'),
            ]
