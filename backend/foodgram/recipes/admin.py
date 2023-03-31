from django.contrib import admin

from .models import Cart, Favorite, Ingredient, IngredientAmount, Recipe, Tag


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
        return Recipe.objects.filter(favorite__recipe_id=obj).count()


@admin.register(Ingredient)
class IngridientAdmit(admin.ModelAdmin):
    """Admin model for Ingredient."""
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(IngredientAmount)
class IngridientAmountAdmit(admin.ModelAdmin):
    """Admin model for IngredientAmount."""
    list_display = ('recipe', 'ingredient', )
    list_filter = ('recipe',)


@admin.register(Tag)
class TagAdmit(admin.ModelAdmin):
    """Admin model for Tag."""
    list_display = ('name', 'color', 'slug',)
    list_filter = ('name',)


@admin.register(Favorite)
class FavoriteAdmit(admin.ModelAdmin):
    """Admin model for Favorite."""
    list_display = ('user', 'recipe',)
    list_filter = ('user',)


@admin.register(Cart)
class CartAdmit(admin.ModelAdmin):
    """Admin model for Favorite."""
    list_display = ('user', 'recipe',)
    list_filter = ('user',)
