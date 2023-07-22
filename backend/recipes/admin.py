from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


class IngredientRecipeInLine(admin.TabularInline):
    model = models.IngredientRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInLine,)
    list_display = ('name', 'author', 'get_html_image', 'get_favorite_amount')
    list_display_links = ('name', 'author', 'get_html_image',)
    list_filter = ('author', 'name', 'tags')
    save_on_top = True

    def get_html_image(self, object):
        return mark_safe(f"<img src='{object.image.url}' width=50>")

    get_html_image.short_description = 'Фотофуд'  # type: ignore

    def get_favorite_amount(self, object):
        return models.FavoriteRecipes.objects.filter(recipe=object).count()

    get_favorite_amount.short_description = 'В избранном'  # type: ignore


class IngredientAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInLine,)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('^name',)


admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Tag)
admin.site.register(models.FavoriteRecipes)
admin.site.register(models.IngredientRecipe)
admin.site.register(models.ShoppingCart)

admin.site.site_title = 'Админка сайта FOODGRAM'
admin.site.site_header = 'Админка сайта FOODGRAM'
