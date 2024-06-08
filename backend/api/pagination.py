from rest_framework.pagination import PageNumberPagination

from api.constants import PAGE_SIZE


class FoodGramPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
