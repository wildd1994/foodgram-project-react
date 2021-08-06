from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FoodgramUser, Follow


class FollowAdmin(admin.ModelAdmin):
    list_display = ['author', 'user']


admin.site.register(FoodgramUser, UserAdmin)
admin.site.register(Follow, FollowAdmin)
