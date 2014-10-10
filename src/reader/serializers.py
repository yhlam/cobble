from rest_framework import serializers

from .models import Entry, Feed


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('name', 'homepage')


class EntrySerializer(serializers.ModelSerializer):
    feed = FeedSerializer(read_only=True)

    class Meta:
        model = Entry
        fields = ('id', 'feed', 'title', 'content', 'link', 'time', 'read')


class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(read_only=True)
