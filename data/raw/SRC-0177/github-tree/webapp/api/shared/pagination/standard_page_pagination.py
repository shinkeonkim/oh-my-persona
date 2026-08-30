from rest_framework.pagination import PageNumberPagination


class StandardPagePagination(PageNumberPagination):
    page_size_query_param = "per_page"
    max_page_size = 100
    page_size = 10
