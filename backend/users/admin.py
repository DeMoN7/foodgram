from django.contrib import admin

from .models import Subscription, User

admin.site.register(Subscription)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',)
    list_filter = ('username', 'email',)


admin.site.register(User, UserAdmin)
