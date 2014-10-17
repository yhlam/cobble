from django.contrib import admin
from django.utils.html import format_html

from .models import Feed, Entry, UserEntryState


def url(short_description, urlfield):
    def url_display(obj):
        url = getattr(obj, urlfield)
        return format_html('<a href="{url}">{url}</a>', url=url)
    url_display.allow_tags = True
    url_display.admin_order_field = urlfield
    url_display.short_description = short_description

    return url_display


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', url('URL', 'url'),)
    search_fields = ('name',)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('feed_name', 'title', url('Link', 'link'), 'time',)
    list_display_links = ('feed_name', 'title',)
    list_filter = ('time',)
    date_hierarchy = 'time'
    search_fields = ('feed__name', 'title', 'content',)

    def feed_name(self, entry):
        return entry.feed.name
    feed_name.short_description = 'Feed'
    feed_name.admin_order_field = 'feed__name'


@admin.register(UserEntryState)
class UserEntryStateAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'feed', 'entry_title',
        'read', 'expanded', 'opened', 'starred',
    )
    list_display_links = ('user', 'feed', 'entry_title',)
    list_filter = ('read', 'expanded', 'opened', 'starred',)
    list_select_related = ('user', 'entry', 'entry__feed',)
    search_fields = ('entry__title',)

    def feed(self, user_entry_state):
        return user_entry_state.entry.feed.name
    feed.short_description = 'Feed'
    feed.admin_order_field = 'entry__feed__name'

    def entry_title(self, user_entry_state):
        return user_entry_state.entry.title
    entry_title.short_description = 'Entry'
    entry_title.admin_order_field = 'entry__title'
