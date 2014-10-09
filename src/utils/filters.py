import django_filters

from .forms import IsoDateTimeField


__all__ = ('IsoDateTimeFilter',)


class IsoDateTimeFilter(django_filters.Filter):
    """Support filter by ISO-8601 formatted date"""
    field_class = IsoDateTimeField
