import hashlib

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import Profile
from .constants import (
    INGREDIENT_NAME,
    INGREDIENT_MEASURE,
    TAG_NAME,
    TAG_SLUG,
    RECIPE_NAME,
    COOKING_TIME_MIN,
    COOKING_TIME_MAX,
    INGREDIENT_AMOUNT_MIN,
    INGREDIENT_AMOUNT_MAX,
    SHORT_LINK_HASH
)


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=INGREDIENT_NAME)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=INGREDIENT_MEASURE
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            UniqueConstraint(fields=['name', 'measurement_unit'],
                             name='unique_ingredient')
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=TAG_NAME
    )
    slug = models.SlugField(
        'Уникальный слаг',
        unique=True,
        max_length=TAG_SLUG
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название', max_length=RECIPE_NAME)
    short_link_hash = models.CharField(
        'Хэш короткой ссылки',
        max_length=SHORT_LINK_HASH,
        blank=True
    )
    author = models.ForeignKey(
        Profile,
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор',
    )
    text = models.TextField('Описание')
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                COOKING_TIME_MIN,
                message=f'Минимальное значение {COOKING_TIME_MIN}!'
            ),
            MaxValueValidator(
                COOKING_TIME_MAX,
                message=f'Максимальное значение {COOKING_TIME_MAX}!'
            )
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        recipe_hash = hashlib.md5(
            str(
                self.id
            ).encode()
        ).hexdigest()[:SHORT_LINK_HASH]
        self.short_link_hash = recipe_hash
        super().save(update_fields=['short_link_hash'])

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                INGREDIENT_AMOUNT_MIN,
                message=f'Минимальное значение {INGREDIENT_AMOUNT_MIN}!'
            ),
            MaxValueValidator(
                INGREDIENT_AMOUNT_MAX,
                message=f'Максимальное значение {INGREDIENT_AMOUNT_MAX}!'
            )
        ]
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name} '
            f'({self.ingredient.measurement_unit}) - {self.amount} '
        )


class FavouriteShoppingCartBase(models.Model):
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True


class Favourite(FavouriteShoppingCartBase):
    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное пользователей'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(FavouriteShoppingCartBase):
    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'корзину'
        verbose_name_plural = 'Корзина покупок пользователей'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'
