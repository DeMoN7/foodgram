from rest_framework import response, status


class PaginateResponse:

    def paginate_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
