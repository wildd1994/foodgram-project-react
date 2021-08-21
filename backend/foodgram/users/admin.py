from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class CustomUSerAdmin(UserAdmin):
    list_filter = ('username', 'email')


admin.site.register(User, CustomUSerAdmin)
