from django.contrib import admin
from .models import AnnouncementCategory, Announcement, AnnouncementRead, Event, EventRegistration

@admin.register(AnnouncementCategory)
class AnnouncementCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'posted_by', 'target_audience', 'is_active', 'is_pinned', 'posted_at']
    list_filter = ['is_active', 'is_pinned', 'priority', 'target_audience', 'category', 'posted_at']
    search_fields = ['title', 'content', 'posted_by__username']
    raw_id_fields = ['posted_by', 'category', 'target_department']
    date_hierarchy = 'posted_at'
    list_editable = ['is_active', 'is_pinned']

@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['user__username', 'announcement__title']
    raw_id_fields = ['announcement', 'user']
    readonly_fields = ['read_at']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'venue', 'organizer', 'target_audience', 'registration_required', 'is_active']
    list_filter = ['is_active', 'target_audience', 'registration_required', 'event_date']
    search_fields = ['title', 'venue', 'organizer__username']
    raw_id_fields = ['organizer', 'target_department']
    date_hierarchy = 'event_date'

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'student', 'registered_at', 'attended']
    list_filter = ['attended', 'registered_at']
    search_fields = ['student__username', 'event__title']
    raw_id_fields = ['event', 'student']
    readonly_fields = ['registered_at']
