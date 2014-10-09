from django.views.generic import TemplateView

import django_filters
from rest_framework.generics import ListAPIView
from rest_framework.filters import DjangoFilterBackend
from rest_framework import ISO_8601


from utils.filters import IsoDateTimeFilter
from .models import Entry
from .serializers import EntrySerializer


class EntryFilterSet(django_filters.FilterSet):
    last_updated = IsoDateTimeFilter(
        name='updated',
        lookup_type='lt',
        input_formats=(ISO_8601,),
    )

    offset = django_filters.NumberFilter(
        decimal_places=0,
        min_value=0,
        action=lambda qs, value: qs[int(value):],
    )

    limit = django_filters.NumberFilter(
        decimal_places=0,
        min_value=0,
        max_value=100,
        action=lambda qs, value: qs[:int(value)],
        required=True,
    )

    class Meta:
        model = Entry
        fields = ['last_updated', 'offset', 'limit']


class EntryListAPIView(ListAPIView):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    filter_class = EntryFilterSet
    filter_backends = (DjangoFilterBackend,)


class ReaderView(TemplateView):
    template_name = 'reader.html'
