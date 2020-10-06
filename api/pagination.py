from rest_framework import pagination
from rest_framework.response import Response

import math


class CustomPageNumber(pagination.PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'page_size': self.page_size,
                'pages': math.ceil(self.page.paginator.count / self.page_size),
                'page': self.page.number,
                'count': self.page.paginator.count
            },
            'results': data,
        })
