from rest_framework.generics import ListAPIView

from .models import Entry
from .serializers import EntrySerializer, PaginatedEntrySerializer


class EntryListAPIView(ListAPIView):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    pagination_serializer_class = PaginatedEntrySerializer
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100

    def get_queryset(self):
        before = self.get_param('before')
        max_id = self.get_param('max_id')
        if before:
            return Entry.objects.filter(time__lt=before, id__lt=max_id)
        else:
            return Entry.objects.all()

    def get_param(self, key):
        kwargs = self.kwargs.get(key)
        if kwargs:
            return kwargs

        query_param = self.request.QUERY_PARAMS.get(key)
        return query_param

    def paginate_queryset(self, queryset, page_size=None):
        self.kwargs[self.page_kwarg] = 1
        return super().paginate_queryset(queryset, page_size)
