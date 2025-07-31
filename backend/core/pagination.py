"""
Custom pagination classes for FOODGRAM project.
"""
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination class with configurable page size."""

    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100

