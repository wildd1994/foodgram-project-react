from django.db import models
from django.contrib.auth.models import AbstractUser


class FoodgramUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)


    class Meta:
        ordering = ('id',)
