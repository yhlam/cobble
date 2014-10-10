from django.db import models

import jsonfield


class Feed(models.Model):
    name = models.CharField(max_length=1024)
    url = models.URLField()
    homepage = models.URLField()
    etag = models.CharField(max_length=1024, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.url)


class Entry(models.Model):
    feed = models.ForeignKey(Feed)
    entry_id = models.CharField(max_length=1024)
    title = models.CharField(max_length=1024)
    content = models.TextField()
    link = models.URLField()
    time = models.DateTimeField()
    json = jsonfield.JSONField()
    updated = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)

    class Meta:
        unique_together = (('feed', 'entry_id'),)
        verbose_name_plural = 'entries'
        ordering = ['-time']

    def __str__(self):
        return '[{}] {}'.format(self.feed.name, self.title)
