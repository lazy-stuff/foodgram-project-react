from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientsViewSet,
    RecipeViewSet,
    TagsViewSet,
    UserViewSet
)


api_router = DefaultRouter()

api_router.register('users', UserViewSet)
api_router.register('tags', TagsViewSet)
api_router.register('ingredients', IngredientsViewSet),
api_router.register('recipes', RecipeViewSet),

urlpatterns = [
    path('', include(api_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
