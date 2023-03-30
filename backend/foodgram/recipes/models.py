from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()


class Ingredient(models.Model):
    """Model for igredients."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=30,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Model for tags to systemize recipes."""

    name = models.CharField(
        verbose_name='Название тега',
        max_length=30,
        unique=True
    )
    color = ColorField(
        verbose_name='Цвет тега',
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.slug


class Recipe(models.Model):
    """Model for recipes."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes_images/'
    )
    name = models.CharField(
        verbose_name='Название блюда',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Описание процесса приготовления'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в мин.',
        validators=[MinValueValidator(1,
                    message='Минимальное время приготовления - 1 мин.')]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class IngredientAmount(models.Model):
    """Model for amount of ingredient in a recipe."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_amount',
        verbose_name='Рецепт'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1,
                              message='Минимальное количество - 1.'),
            MaxValueValidator(10000,
                              message='Максимальное количество - 10000.')
                    ]
    )

    class Meta:
        verbose_name = 'Количество ингредиентов в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe_ingredient'
            ),
        ]

    def __str__(self) -> str:
        return f'В рецепте {self.recipe.name} есть {self.ingredient.name}'


class Favorite(models.Model):
    """Model for users' favorite recipes."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user.username} добавил {self.recipe.name} в избранное'


class Cart(models.Model):
    """Model for keeping chosen recipes and ingredients for cooking."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user.username} добавил {self.recipe.name} в корзину'
