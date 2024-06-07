from django.db import transaction
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from .models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.serializers import ProfileSerializer


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = ProfileSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
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
            'cooking_time',
        )

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        return (
                user and
                user.is_authenticated and
                user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        return (
                user and
                user.is_authenticated and
                user.shopping_cart.filter(recipe=obj).exists()
        )


class IngredientInRecipeWriteSerializer(ModelSerializer):
    id = IntegerField(write_only=True, required=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True, required=True)
    author = ProfileSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True, required=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_image(self, value):
        if not value:
            raise ValidationError(
                {'image': 'Не предоставлена картинка рецепта'}
            )

        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                {'ingredients': 'Нужен хотя бы один ингредиент'}
            )

        ingredients_list = []

        for item in value:
            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    {'ingredients': 'Такого ингредиента нет в нашей базе'}
                )

            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients': 'Ингридиенты не могут повторяться'}
                )

            if int(item['amount']) <= 0:
                raise ValidationError(
                    {'amount': 'Количество ингредиента должно быть больше 0!'}
                )

            ingredients_list.append(ingredient)

        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег!'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Теги должны быть уникальными!'}
                )
            tags_list.append(tag)
        return value

    @transaction.atomic
    def create_ingredients_amounts(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
        else:
            raise ValidationError(
                {'tags': 'Нужно выбрать хотя бы один тег!'}
            )

        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
        else:
            raise ValidationError(
                {'ingredients': 'Нужен хотя бы один ингредиент'}
            )

        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance,
            ingredients=ingredients
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data
