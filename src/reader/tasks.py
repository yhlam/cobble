import asyncio
from collections import namedtuple
from datetime import datetime
from email.utils import format_datetime, parsedate_to_datetime
import time
import logging

from django.utils import timezone

import aiohttp
from aiohttp.errors import ConnectionError, HttpException
import feedparser

from .models import Feed, Entry


log = logging.getLogger('reader.tasks')


FeedResponse = namedtuple(
    'FeeedResponse',
    ['etag', 'last_modified', 'entries']
)


def load_all_feeds():
    _load_feeds(Feed.objects.all())


def load_feed(feed):
    _load_feeds((feed,))


def _load_feeds(feeds):
    loop = asyncio.new_event_loop()
    tasks = [_load_feed_async(feed, loop) for feed in feeds]
    loop.run_until_complete(asyncio.wait(tasks, loop=loop))
    loop.close()


@asyncio.coroutine
def _load_feed_async(feed, loop=None):
    try:
        response = yield from _fetch_entries(feed, loop)
    except Exception:
        log.exception('Failed to fetch entries for feed %s', feed)
    else:
        if response:
            _process_entries(feed, *response)


@asyncio.coroutine
def _fetch_entries(feed, loop=None):
    url = feed.url
    request_etag = feed.etag
    request_last_modified = feed.last_modified

    response = yield from _request_entries(
        url,
        etag=request_etag,
        last_modified=request_last_modified,
        loop=loop
    )

    if response is None:
        log.info('%s is not modified', feed)
        return None

    response_headers, xml = response

    etag = response_headers.get('etag','')
    if isinstance(etag, bytes):
        etag = etag.decode('utf-8', 'ignore')

    last_modified = response_headers.get('last-modified')
    if last_modified:
        last_modified = parsedate_to_datetime(last_modified)

    data = feedparser.parse(xml)

    return FeedResponse(etag, last_modified, data.entries)


@asyncio.coroutine
def _request_entries(url, etag=None, last_modified=None, fail_fast=False,
                     loop=None):
    headers = {'A-IM': 'feed'}  # RFC 3229 support
    if etag:
        headers['If-None-Match'] = etag
    if last_modified:
        headers['If-Modified-Since'] = format_datetime(last_modified)

    try:
        response = yield from aiohttp.request(
            'get', url, headers=headers, loop=loop,
        )

        if response.status == 304:
            return None

        try:
            xml = yield from response.text()
        except:
            content = yield from response.read()
            charset = 'utf-8'
            content_type = response.headers.get('Content-Type')
            parts = content_type.split(';')
            if len(parts) > 1:
                for part in parts[1:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        if key.lower().strip() == 'charset':
                            charset = value
            xml = content.decode(charset)

        return response.headers, xml

    except (ConnectionError, HttpException):
        if fail_fast:
            raise

        if etag and last_modified:
            # try etag only
            try:
                response = yield from _request_entries(
                    url, etag=etag, fail_fast=True, loop=loop
                )
            except (ConnectionError, HttpException):
                pass
            else:
                return response

            # try last modified only
            try:
                response = yield from _request_entries(
                    url, last_modified=last_modified, fail_fast=True, loop=loop
                )
            except (ConnectionError, HttpException):
                pass
            else:
                return response

        if etag or last_modified:
            # try without etag and last modified
            response = yield from _request_entries(
                url, fail_fast=True, loop=loop
            )
            return response
        else:
            raise



def _process_entries(feed, etag, last_modified, entries):
    feed.etag = etag
    feed.last_modified = last_modified
    feed.save()

    success = 0
    for entry in entries:
        try:
            _process_entry(feed, entry)
        except Exception:
            log.exception('Encounter exception while processing entry: %s',
                          entry)
        else:
            success += 1

    log.info('Updated %d entries for %s', success, feed)


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
            'json': entry,
        }
    )


def _get_value(entry, *fields):
    for field in fields:
        value = entry.get(field)
        if value:
            return value
