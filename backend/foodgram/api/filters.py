from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe
from rest_framework.filters import SearchFilter
from users.models import CustomUser


class IngredientsFilter(SearchFilter):
    """Search filter for ingredients."""

    search_param = 'name'


class RecipesFilter(FilterSet):
    """Filter for recipes."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        return (queryset.filter(favorite__user=self.request.user)
                if value and not self.request.user.is_anonymous
                else queryset)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return (queryset.filter(cart__user=self.request.user)
                if value and not self.request.user.is_anonymous
                else queryset)
