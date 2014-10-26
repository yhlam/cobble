import pickle

from django.conf import settings
from django.db import models

from reader.models import Entry, UserEntryState
from . import prioritizers


class Prioritizer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    model = models.BinaryField()
    buildtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Prioritizer {} @ {:%Y-%m-%d %H:%M:%S}'.format(
            self.user.username, self.buildtime
        )


class UserEntryPriority(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    entry = models.ForeignKey(Entry)
    priority = models.FloatField()

    def __str__(self):
        return '{{userid: {}, entryid: {}, priority: {}}}'.format(
            self.user.id, self.entry.id, self.priority
        )

    class Meta:
        unique_together = (('user', 'entry'),)
        verbose_name_plural = 'user_entry_priorities'
