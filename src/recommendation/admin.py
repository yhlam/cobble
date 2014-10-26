from django.contrib import admin

from .models import Prioritizer, UserEntryPriority


@admin.register(Prioritizer)
class PrioritizerAdmin(admin.ModelAdmin):
    list_display = ('user', 'buildtime',)


@admin.register(UserEntryPriority)
class UserEntryPriorityAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry_title', 'priority',)
    list_display_links = ('user', 'entry_title', 'priority',)
    search_fields = ('user__username', 'entry__title',)

    def entry_title(self, priority):
        return priority.entry.title
    entry_title.short_description = 'Entry'
    entry_title.admin_order_field = 'entry__title'
