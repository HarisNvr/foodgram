from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .serializers import ShoppingCartSerializer, FavoriteSerializer
from recipes.models import (
    Favourite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from .filters import IngredientFilter, RecipeFilter
from .pagination import FoodGramPagination
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer
)
from .permissions import IsAuthorAdminOrReadOnly


def redirect_to_recipe(request, recipe_hash):
    recipe = get_object_or_404(Recipe, short_link_hash=recipe_hash)
    relative_url = '/recipes/' + str(recipe.pk) + '/'
    full_url = request.build_absolute_uri(relative_url)
    return HttpResponseRedirect(full_url)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    http_method_names = ['get']


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorAdminOrReadOnly,)
    pagination_class = FoodGramPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        recipe_hash = recipe.short_link_hash
        short_link = request.build_absolute_uri(
            reverse(
                'short-link-redirect',
                args=[recipe_hash]
            )
        )

        return Response({'short-link': short_link})

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        context = {'request': request}
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = FavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = Favourite.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()

        if obj == (0, {}):
            return Response({'errors': 'Рецепт не найден в вашем избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        context = {'request': request}
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()

        if obj == (0, {}):
            return Response({'errors': 'Рецепт не найден в вашей корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
