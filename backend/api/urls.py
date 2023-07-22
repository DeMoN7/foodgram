from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientsViewSet, RecipesViewSet, TagViewSet, UsersViewSet

router = DefaultRouter()
router.register('ingredients', IngredientsViewSet)
router.register('recipes', RecipesViewSet)
router.register('tags', TagViewSet)
router.register('users', UsersViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
