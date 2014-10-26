import pickle

from django.contrib.auth import get_user_model
from celery import shared_task

from reader.models import Entry, UserEntryState
from .models import Prioritizer, UserEntryPriority
from . import prioritizers


User = get_user_model()


@shared_task
def build_prioritizer(userid):
    user = User.objects.get(id=userid)
    states = UserEntryState.objects.select_related(
        'user', 'entry'
    ).filter(user=user, read=True)

    model = prioritizers.build(states)
    pickled_model = pickle.dumps(model)
    Prioritizer.objects.update_or_create(
        user=user,
        defaults={
            'model': pickled_model
        },
    )


@shared_task
def build_all_prioritizers():
    users = User.objects.all()
    for user in users:
        build_prioritizer(user.id)


@shared_task
def prioritize(entryids):
    entries = Entry.objects.select_related(
        'feed', 'feed__subscribers'
    ).filter(id__in=entryids)
    feeds = {entry.feed for entry in entries}
    users = {subscriber
             for feed in feeds
             for subscriber in feed.subscribers.all()}
    prioritizers = {
        prioritizer.user.id: pickle.loads(prioritizer.model)
        for prioritizer in Prioritizer.objects.filter(user__in=users)
    }

    prioritize_for_entries_and_priortizers(entries, prioritizers)


def prioritize_for_entries_and_priortizers(entries, prioritizers):
    for entry in entries:
        for subscriber in entry.feed.subscribers.all():
            prioritizer = prioritizers.get(subscriber.id)
            if prioritizer:
                score = prioritizer.prioritize(entry)
                UserEntryPriority.objects.get_or_create(
                    user=subscriber, entry=entry, defaults={'priority': score}
                )


@shared_task
def prioritize_all_entries():
    entries = Entry.objects.select_related(
        'feed', 'feed__subscribers'
    ).all()

    prioritizers = {
        prioritizer.user.id: pickle.loads(prioritizer.model)
        for prioritizer in Prioritizer.objects.all()
    }

    prioritize_for_entries_and_priortizers(entries, prioritizers)
