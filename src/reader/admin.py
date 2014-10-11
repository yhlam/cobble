from django.contrib import admin

from .models import Feed, Entry, UserEntryState

admin.site.register(Feed)
admin.site.register(Entry)
admin.site.register(UserEntryState)
