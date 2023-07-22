from django_filters import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для рецептов: по тегам, автору, избранному и списку покупок"""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.NumberFilter(
        field_name='author',
        lookup_expr='exact',
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='is_in_shopping_cart_filter',
    )
    is_favorited = filters.NumberFilter(
        method='is_favorited_filter',
    )

    class Meta:
        model = Recipe
        fields = ('tags',)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_recipes__user=self.request.user)
        return queryset

    def is_favorited_filter(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """Кастомный фильтр для ингрединтов"""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
