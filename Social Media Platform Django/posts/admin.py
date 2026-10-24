from django.contrib import admin
from django.utils import timezone
from .models import Comment, Like, Post, Report

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'visibility', 'is_hidden', 'created_at']
    list_filter = ['visibility', 'is_hidden']
    search_fields = ['content', 'author__username']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'is_hidden']
    list_filter = ['is_hidden']
    search_fields = ['content']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'post', 'comment', 'status', 'reviewed_by']
    list_filter = ['status']
    readonly_fields = ['reporter', 'post', 'comment', 'reason', 'created_at', 'reviewed_by', 'reviewed_at']
    actions = ['hide_content', 'dismiss_reports']

    @admin.action(description='Hide reported content and resolve reports')
    def hide_content(self, request, queryset):
        for report in queryset.filter(status='pending'):
            target = report.post or report.comment
            target.is_hidden = True
            target.save(update_fields=['is_hidden'])
            report.status = 'resolved'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()

    @admin.action(description='Dismiss selected reports')
    def dismiss_reports(self, request, queryset):
        queryset.filter(status='pending').update(status='dismissed', reviewed_by=request.user, reviewed_at=timezone.now())

admin.site.register(Like)
