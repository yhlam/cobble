from django.conf import settings
from django.db import models

import jsonfield


class Feed(models.Model):
    name = models.CharField(max_length=1024)
    url = models.URLField()
    homepage = models.URLField()
    etag = models.CharField(max_length=1024, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='feeds',
        related_query_name='feed',
    )

    def __str__(self):
        return '{} ({})'.format(self.name, self.url)


class Entry(models.Model):
    feed = models.ForeignKey(Feed)
    entry_id = models.CharField(max_length=1024)
    title = models.CharField(max_length=1024)
    content = models.TextField()
    link = models.URLField(max_length=1024)
    time = models.DateTimeField()
    json = jsonfield.JSONField()
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('feed', 'entry_id'),)
        verbose_name_plural = 'entries'
        ordering = ['-time']

    def __str__(self):
        return '[{}] {}'.format(self.feed.name, self.title)


class UserEntryState(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='entry_states',
        related_query_name='entry_state'
    )
    entry = models.ForeignKey(
        Entry,
        related_name='user_states',
        related_query_name='user_state'
    )
    read = models.BooleanField(default=False)
    expanded = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    starred = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.user.username, self.entry.title)
