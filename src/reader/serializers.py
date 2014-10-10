from rest_framework import serializers

from .models import Entry


class EntrySerializer(serializers.ModelSerializer):
    feed = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Entry
        fields = ('id', 'feed', 'title', 'content', 'link', 'time', 'read')


class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(read_only=True)
