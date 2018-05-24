from rest_framework import pagination


class PageSizedPagination(pagination.PageNumberPagination):
    """
    Pagination subclass to all to control the page size
    """
    page_size_query_param = 'page_size'
    all_pages_strings = ('all',)
    max_page_size = 10000

    def get_page_size(self, request):
        try:
            page_size_str = request.query_params[self.page_size_query_param]
            if page_size_str in self.all_pages_strings:
                return self.max_page_size
        except KeyError:
            pass

        return super(PageSizedPagination, self).get_page_size(request)
