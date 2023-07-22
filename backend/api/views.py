from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    FavoriteRecipes,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientsSerializer,
    RecipeCreateSerializer,
    RecipeFollowSerializer,
    RecipesSerializer,
    SetPasswordSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer
)
from .utils import get_ingredients_for_file

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """Представление для пользователей, работа со всеми эндпойнтами users/"""
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action == 'create':
            return (AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer

    def get_instance(self):
        return self.request.user

    @action(detail=False, url_path='me', url_name='me',
            permission_classes=(IsAuthenticated,))
    def get_current_user(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=False,
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        current_user.set_password(serializer.data["new_password"])
        current_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        current_user = self.request.user
        subscriptions = User.objects.filter(follow__user=current_user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk):
        current_user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'DELETE':
            get_object_or_404(
                Subscription, user=current_user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SubscriptionSerializer(
            author,
            data=request.data,
            context={'request': request, 'author': author})
        serializer.is_valid(raise_exception=True)
        Subscription.objects.create(user=current_user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов, только на чтение"""
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тегов, только на чтение"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Представление для рецептов, работа со всеми эндпойнтами recipes/"""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipesSerializer
        return RecipeCreateSerializer

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            get_object_or_404(
                FavoriteRecipes, user=current_user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = RecipeFollowSerializer(recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        FavoriteRecipes.objects.create(user=current_user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            get_object_or_404(
                ShoppingCart, user=current_user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = RecipeFollowSerializer(recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        ShoppingCart.objects.create(user=current_user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_recipes__user=request.user)
        response = HttpResponse(
            get_ingredients_for_file(ingredients), headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': 'attachment', })
        return response
