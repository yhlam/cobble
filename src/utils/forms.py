from django import forms
from django.utils.dateparse import parse_datetime
from django.utils.encoding import force_str

from rest_framework import ISO_8601
from rest_framework import serializers


__all__ = ('IsoDateTimeField',)


class IsoDateTimeField(forms.DateTimeField):
    """Support ISO-8601 date format"""

    def strptime(self, value, format):
        value = force_str(value)
        if format == ISO_8601:
            parsed = parse_datetime(value)
            if parsed is None:
                err = "time data '{}' does not ISO-8601 format".format(value)
                raise ValueError(err)

            return parsed

        return super(IsoDateTimeField, self).strptime(value, format)
