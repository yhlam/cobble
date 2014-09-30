from rest_framework import serializers
from rest_framework import pagination
from rest_framework.templatetags.rest_framework import replace_query_param

from .models import Entry


class EntrySerializer(serializers.ModelSerializer):
    feed = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Entry
        fields = ('feed', 'title', 'content', 'link', 'time')


class NextEntryPageField(serializers.Field):
    def to_native(self, object_list):
        if not object_list:
            return None

        last_entry = list(object_list)[-1]
        before = self.format_time(last_entry.time)
        request = self.context.get('request')
        url = request and request.build_absolute_uri() or ''
        replaced_before = replace_query_param(url, 'before', before)
        return replace_query_param(replaced_before, 'max_id', last_entry.id)

    def format_time(self, time):
        ret = time.isoformat()
        if ret.endswith('+00:00'):
            ret = ret[:-6] + 'Z'
        return ret


class PaginatedEntrySerializer(pagination.BasePaginationSerializer):
    next = NextEntryPageField(source='object_list')
    before = serializers.DateTimeField(write_only=True)
    max_id = serializers.IntegerField(write_only=True)
