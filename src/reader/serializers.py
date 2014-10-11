from rest_framework import fields
from rest_framework import serializers

from .models import Entry, Feed, UserEntryState


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('name', 'homepage')


class ReadField(fields.BooleanField):
    read_only = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def field_to_native(self, obj, field_name):
        if obj is None:
            return self.empty

        request = self.context['request']

        try:
            state = obj.user_states.get(user=request.user)
        except UserEntryState.DoesNotExist:
            return self.to_native(False)
        else:
            return self.to_native(state.read)


class EntrySerializer(serializers.ModelSerializer):
    feed = FeedSerializer(read_only=True)
    read = ReadField()

    class Meta:
        model = Entry
        fields = ('id', 'feed', 'title', 'content', 'link', 'time', 'read')


class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(read_only=True)
