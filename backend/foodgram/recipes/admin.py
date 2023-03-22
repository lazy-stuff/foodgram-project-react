from django.contrib import admin

from .models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    Tag
)


class IngredientInlineAdmin(admin.TabularInline):
    """Admin inline model for Ingredient."""
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmit(admin.ModelAdmin):
    """Admin model for Recipe."""

    list_display = ('name', 'author', 'is_in_favorites',)
    list_filter = ('author', 'name', 'tags',)
    inlines = (IngredientInlineAdmin,)

    def is_in_favorites(self, obj):
        result = Recipe.objects.filter(favorite__recipe_id=obj).count()
        return result


@admin.register(Ingredient)
class IngridientAdmit(admin.ModelAdmin):
    """Admin model for Ingredient."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Cart)
admin.site.register(Favorite)
admin.site.register(IngredientAmount)
admin.site.register(Tag)
