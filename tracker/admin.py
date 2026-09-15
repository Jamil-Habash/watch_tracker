from django.contrib import admin

from .models import ShowEntry


@admin.register(ShowEntry)
class ShowEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "status", "year", "rating", "user", "date_watched")
    list_filter = ("type", "status", "user")
    search_fields = ("title", "notes")
    list_per_page = 25
    date_hierarchy = "date_watched"
    ordering = ("-date_watched",)
    fieldsets = (
        ("Title", {"fields": ("title", "type")}),
        ("Status", {"fields": ("status", "year", "rating", "date_watched")}),
        ("Episode Tracking", {"fields": ("ep_current", "ep_total")}),
        ("Details", {"fields": ("notes",)}),
        ("Ownership", {"fields": ("user",)}),
    )