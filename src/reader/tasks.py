from django.utils import timezone

from collections import namedtuple
from datetime import datetime
import time
import logging

import feedparser

from .models import Feed, Entry


log = logging.getLogger('reader.tasks')


FeedResponse = namedtuple(
    'FeeedResponse',
    ['etag', 'last_modified', 'entries']
)


def load_all_feeds():
    for feed in Feed.objects.all():
        load_feed(feed)


def load_feed(feed):
    response = _fetch_entries(feed)
    if response:
        _process_entries(feed, *response)


def _fetch_entries(feed):
    data = feedparser.parse(
        feed.url,
        etag=(feed.etag or None),
        modified=feed.last_modified
    )

    if data.get('status') == 304:
        return None
    else:
        etag = data.get('etag', '')
        last_modified = data.get('modified_parsed', None)
        if last_modified:
            last_modified = datetime(*last_modified[:6], tzinfo=timezone.utc)
        return FeedResponse(etag, last_modified, data.entries)


def _process_entries(feed, etag, last_modified, entries):
    feed.etag = etag
    feed.last_modified = last_modified
    feed.save()

    for entry in entries:
        try:
            _process_entry(feed, entry)
        except Exception:
            log.exception('Encounter exception while processing entry: %s',
                          entry)


def _process_entry(feed, entry):
    try:
        link = entry.link
    except KeyError:
        log.warning('Missing link, skiped entry: %s', entry)
        return

    try:
        title = entry.title
    except KeyError:
        log.warning('Missing title, skiped entry: %s', entry)
        return

    content = _get_value(entry, 'content', 'summary') or ''

    entry_timestruct = _get_value(
        entry,
        'updated_parsed', 'pubished_parsed', 'created_parsed'
    ) or time.gmtime()
    entry_time = datetime(*entry_timestruct[:6], tzinfo=timezone.utc)

    entry_id = entry.get('id', link)

    Entry.objects.get_or_create(
        feed=feed,
        entry_id=entry_id,
        defaults={
            'time': entry_time,
            'title': title,
            'content': content,
            'link': link,
        }
    )


def _get_value(entry, *fields):
    for field in fields:
        value = entry.get(field)
        if value:
            return value
