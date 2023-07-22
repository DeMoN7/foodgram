import re

from django.contrib.auth import get_user_model
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError

from recipes import models
from users.models import Subscription

from .utils import Base64ImageField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Для отображения пользователей"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(
                user=user, author=obj.pk).exists()
        return False

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')


class UserCreateSerializer(serializers.ModelSerializer):
    """Для отображения нужных полей при регистрации пользователя"""
    password = serializers.CharField(write_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise ValidationError('Недопустимые символы в поле username')
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],)
        user.set_password(validated_data['password'])
        user.save()
        return user


class SetPasswordSerializer(serializers.Serializer):
    """Для отображения нужных полей при смене пароля"""
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, attrs):
        print(self.context["request"].user)
        is_password_valid = self.context["request"].user.check_password(
            attrs['current_password'])
        if attrs['current_password'] == attrs['new_password']:
            raise ValidationError('Новый пароль должен отдичаться от старого')
        if not is_password_valid:
            raise ValidationError('Текущий пароль неверный')
        return attrs


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Для отображения ингредиентов с доп.полями в рецептах"""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = models.IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class IngredientsSerializer(serializers.ModelSerializer):
    """Для отображения ингредиентов"""
    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Для отображения тегов"""
    class Meta:
        model = models.Tag
        fields = '__all__'


class RecipesSerializer(serializers.ModelSerializer):
    """Для отображения рецептов с доп.полями"""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return models.FavoriteRecipes.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return models.ShoppingCart.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def get_ingredients(self, obj):
        ingredients = models.IngredientRecipe.objects.filter(recipe=obj)
        serializer = IngredientRecipeSerializer(ingredients, many=True)
        return serializer.data


class IngredientMiniSerializer(serializers.Serializer):
    """Вложенный сериализатор для полей ингредиентов при создании рецепта"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Для отображения нужных полей при создании рецепта"""
    ingredients = IngredientMiniSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Ingredient.objects.all(),
                fields=['ingredients']
            )
        ]

    def validate_ingredients(self, value):
        tmp_list = []
        for i in range(len(value)):
            if value[i]['id'] not in tmp_list:
                tmp_list.append(value[i]['id'])
            else:
                ingredient_name = models.Ingredient.objects.get(
                    id=value[i]['id'])
                raise ValidationError(
                    f'Ингредиент: <{ingredient_name}> добавлен более одного '
                    'раза, а так делать нельзя')
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise ValidationError('Время приготовления от 1 минуты')
        return value

    def ingredients_and_tags_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(models.IngredientRecipe(
                ingredients=models.Ingredient.objects.get(
                    pk=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']))
        models.IngredientRecipe.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(
            author=self.context['request'].user, **validated_data)
        self.ingredients_and_tags_set(recipe, tags_data, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        models.IngredientRecipe.objects.filter(
            recipe=instance,
            ingredients__in=instance.ingredients.all()).delete()
        self.ingredients_and_tags_set(instance, tags_data, ingredients_data)
        instance.save()
        return instance


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор для рецептов в подписках пользователя"""
    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Для отображения подпискок пользователя"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        recipes = models.Recipe.objects.filter(author=obj)
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit:
            serializer = RecipeFollowSerializer(
                recipes[:int(recipes_limit)], many=True)
            return serializer.data
        serializer = RecipeFollowSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        count = models.Recipe.objects.filter(author=obj).count()
        return count

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, attrs):
        user = self.context['request'].user
        author = self.context.get('author')
        if user == author:
            raise ValidationError(
                'Нелья подписаться на самого себя')
        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                'подписка на данного пользавателя уже существует')
        return attrs
