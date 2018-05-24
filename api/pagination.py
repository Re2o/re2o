from rest_framework import pagination
from django.core import paginator
from django.utils.functional import cached_property


class AllowNegativePaginator(paginator.Paginator):
    """
    Paginator subclass to allow negative or null `per_page` argument,
    meaning to show all items in one page.
    """
    def page(self, number):
        """
        Bypass the default page creation to render all items if `per_page`
        argument is negative or null.
        """
        if self.per_page <= 0:
            return self._get_page(self.object_list, 1, self)
        return super(AllowNegativePaginator, self).page(number)

    @cached_property
    def num_pages(self):
        """
        Bypass the default number of page to return 1 if `per_page` argument
        is negative or null.
        """
        if self.per_page <= 0:
            return 1
        return super(AllowNegativePaginator, self).num_pages


class PageSizedPagination(pagination.PageNumberPagination):
    """
    Pagination subclass to all to control the page size
    """
    page_size_query_param = 'page_size'
    all_pages_strings = ('all',)
    django_paginator_class = AllowNegativePaginator

    def get_page_size(self, request):
        try:
            page_size_str = request.query_params[self.page_size_query_param]
            if page_size_str in self.all_pages_strings:
                return -1
        except KeyError:
            pass

        return super(PageSizedPagination, self).get_page_size(request)
