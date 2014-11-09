from rest_framework import fields
from rest_framework import serializers

from .models import Entry, Feed, UserEntryState, UserConfig


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('name', 'homepage')


class EntryStateField(fields.BooleanField):
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
            source = self.source or field_name
            value = state

            for component in source.split('.'):
                value = fields.get_component(state, component)
                if value is None:
                    break

            return self.to_native(value)


class EntrySerializer(serializers.ModelSerializer):
    feed = FeedSerializer(read_only=True)
    read = EntryStateField()
    starred = EntryStateField()

    class Meta:
        model = Entry
        fields = ('id', 'feed', 'title', 'content', 'link', 'time',
                  'read', 'starred')


class UserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConfig
        fields = ('mode', 'sorting', 'user',)
        write_only_fields = ('user',)


class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(read_only=True)


class FetchOptionSerializer(serializers.Serializer):
    async = serializers.ChoiceField(
        choices=(
            ('T', 'True'),
            ('F', 'False'),
        ),
        blank_display_value='T',
        write_only=True,
    )
