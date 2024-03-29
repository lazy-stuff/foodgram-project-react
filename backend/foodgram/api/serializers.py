from django.db import transaction
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from users.models import CustomUser, Follow


class UserCreateSerializer(BaseUserCreateSerializer):
    """Serializer for Djoser users' authentication."""

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all())])
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'password', 'username', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Djoser user_list."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow Model."""

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only='True',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Follow
        fields = ['user', 'author']
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message=(
                    'Подписаться на обновления автора можно только один раз!'
                )
            ),
        )

    def validate(self, data):
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError(
                'Подписаться на самого себя нельзя!')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag Model."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient Model."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Serializer for IngredientAmount Model."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeReadSerializer(serializers.ModelSerializer):
    """Serializer to GET data from Recipe model."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        ]
        read_only_fields = [
            'ingredients', 'is_favorited', 'is_in_shopping_cart'
        ]

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Cart.objects.filter(recipe=obj, user=user).exists()


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    """Serializer to POST/PATCH/DELETE data for IngredientAmount model."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.values_list('id', flat=True)
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ['id', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer to POST/PATCH/DELETE data for Recipe model."""

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_null=False
    )
    image = Base64ImageField(
        max_length=None,
        required=True,
        use_url=True)
    ingredients = IngredientAmountCreateSerializer(many=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        ]

    def validate(self, data):
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError('Теги указывать обязательно!')
        tags_list = list()
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Теги должны быть уникальными!')
            tags_list.append(tag)

        ingredients = data['ingredients']
        ingredients_list = list()
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторяться!')
            amount = int(ingredient['amount'])
            if amount < 1 or amount > 10000:
                raise serializers.ValidationError(
                    'Слишком маленькое или большое количество ингридиента!')
            ingredients_list.append(ingredient['id'])

        return data

    def create_ingredients(self, ingredients, recipe):
        return IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=Ingredient.objects.get(id=ingredient['id'])
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags_data)
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class ShortenedRecipeSerializer(serializers.ModelSerializer):
    """Serializer for representation of shortened Recipe Model."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoritesSerializer(serializers.ModelSerializer):
    """Serializer for Favorite Model."""

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def validate(self, data):
        user = self.context['request'].user
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortenedRecipeSerializer(
            instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for Cart Model."""

    class Meta:
        model = Cart
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortenedRecipeSerializer(
            instance.recipe, context=context).data


class FollowReadSerializer(UserSerializer):
    """Serializer for users' subscription."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        ]

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj).all()[:3]
        serializer = ShortenedRecipeSerializer(
            recipes,
            many=True,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
