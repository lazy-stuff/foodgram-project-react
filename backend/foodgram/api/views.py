from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from users.models import CustomUser, Follow

from .filters import IngredientsFilter, RecipesFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly, IsOwner
from .serializers import (FavoritesSerializer, FollowReadSerializer,
                          FollowSerializer, IngredientsSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, TagSerializer)


class UserViewSet(DjoserUserViewSet):
    """ViewSet for users/ """

    @action(
        methods=['get'], detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        self.pagination_class = LimitPageNumberPagination
        users = CustomUser.objects.filter(following__user=user)
        paginated_data = self.paginate_queryset(users)
        serializer = FollowReadSerializer(
            data=paginated_data, many=True, context={'request': request}
        )
        serializer.is_valid()
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        id = self.kwargs.get('pk')
        author = get_object_or_404(CustomUser, id=id)
        serializer = FollowSerializer(data={
                                      'user': user.follower,
                                      'author': author
                                      },
                                      context={'request': request}
                                      )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            serializer = FollowReadSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(Follow, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(ReadOnlyModelViewSet):
    """ViewSet for tags/ """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(ReadOnlyModelViewSet):
    """ViewSet for ingredients/ """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for recipes/ """

    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = RecipesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(
        methods=['post'], detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = FavoritesSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_item = get_object_or_404(Favorite, user=user, recipe=recipe)
        model_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'], detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = ShoppingCartSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_item = get_object_or_404(Cart, user=user, recipe=recipe)
        model_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'], detail=False,
        permission_classes=[IsOwner]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient_id__name',
            'ingredient_id__measurement_unit'
        ).order_by('ingredient_id__name').annotate(total=Sum('amount'))
        shopping_cart = list()
        shopping_cart.append('Список покупок: \n')
        for ingredient in ingredients:
            shopping_cart.append(
                f'{ingredient["ingredient_id__name"]} - '
                f'{ingredient["total"]} '
                f'{ingredient["ingredient_id__measurement_unit"]} \n'
            )
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, 'Content-Type: text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
