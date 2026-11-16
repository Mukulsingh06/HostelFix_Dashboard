from django.contrib import admin
from .models import UserProfile, Complaint, ComplaintTimeline, ComplaintComment


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'hostel_block', 'room_number', 'specialization')
    list_filter = ('role', 'hostel_block', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


class TimelineInline(admin.TabularInline):
    model = ComplaintTimeline
    extra = 0
    readonly_fields = ('changed_by', 'old_status', 'new_status', 'note', 'timestamp')


class CommentInline(admin.TabularInline):
    model = ComplaintComment
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'title', 'student', 'category', 'urgency', 'status', 'created_at')
    list_filter = ('status', 'category', 'urgency', 'hostel_block')
    search_fields = ('ticket_id', 'title', 'student__username')
    readonly_fields = ('ticket_id', 'created_at', 'updated_at')
    inlines = [TimelineInline, CommentInline]


@admin.register(ComplaintTimeline)
class ComplaintTimelineAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'changed_by', 'old_status', 'new_status', 'timestamp')
    list_filter = ('new_status',)


@admin.register(ComplaintComment)
class ComplaintCommentAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'author', 'created_at')
