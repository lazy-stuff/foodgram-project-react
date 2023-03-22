from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    Tag
)
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

    user = serializers.IntegerField(source='user.id')
    author = serializers.IntegerField(source='author.id')

    class Meta:
        model = Follow
        fields = ['user', 'author']

    def validate(self, data):
        user = data['user']['id']
        author = data['author']['id']
        if user == author:
            raise serializers.ValidationError(
                'Подписаться на самого себя нельзя!')
        elif Follow.objects.filter(
                user=user,
                author__id=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора!')
        return data

    def create(self, validated_data):
        author = validated_data.get('author')
        author = get_object_or_404(CustomUser, pk=author.get('id'))
        user = validated_data.get('user')
        return Follow.objects.create(user=user, author=author)


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


class IngredientAmountCreateSerializer(IngredientAmountSerializer):
    """Serializer to POST/PATCH/DELETE data for IngredientAmount model."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fileds = ['id', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer to POST/PATCH/DELETE data for Recipe model."""

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(
        max_length=None,
        required=True,
        use_url=True)
    ingredients = IngredientAmountCreateSerializer(many=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        ]

    def validate_tags(self, data):
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError('Теги указывать обязательно!')
        tags_list = list()
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Теги должны быть уникальными!')
            tags_list.append(tag)
        return data

    def validate_ingredients(sel, data):
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

    def validate_cooking_time(self, data):
        cooking_time = data['cooking_time']
        if int(cooking_time) <= 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 мин!')
        return data

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_item = get_object_or_404(
                Ingredient,
                pk=ingredient['id']
            )
            IngredientAmount.objects.create(
                ingredient=ingredient_item,
                recipe=recipe,
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingridients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.clear()
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        self.add_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance

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
        recipes = Recipe.objects.filter(author=obj).all()
        serializer = ShortenedRecipeSerializer(
            recipes,
            many=True,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
