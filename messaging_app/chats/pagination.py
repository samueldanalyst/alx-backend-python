from rest_framework.pagination import PageNumberPagination

class ConversationResultsSetPagination(PageNumberPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 7


from rest_framework.pagination import PageNumberPagination

class MessageResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20