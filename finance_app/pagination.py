"""Shared pagination class so clients can request larger pages.

The stock `PageNumberPagination` ignores `?page_size=` unless a
`page_size_query_param` is set on the class. Without it, list views
that want "give me everything up to 100" (e.g. the detail-page tables
that render the full expense / investment history) had to walk pages
manually in the frontend. One central class + cap keeps that simple
without letting a client request a million rows in one go.
"""

from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
