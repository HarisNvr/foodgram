from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    page_size_query_param = "limit"
