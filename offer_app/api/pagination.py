from rest_framework.pagination import PageNumberPagination


# Custom pagination for offers with page size and limits.
class OfferPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
