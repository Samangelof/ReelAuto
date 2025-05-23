# core/admin.py
from django.contrib import admin
from .models import SearchTask, SearchResult


@admin.register(SearchTask)
class SearchTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'status')
    actions = ['run_task_now']

    @admin.action(description="Запустить задачу сейчас")
    def run_task_now(self, request, queryset):
        for task in queryset:
            # В реальности — отправлю в Celery или вызову API
            task.status = 'processing'
            task.save()
        self.message_user(request, f"{queryset.count()} задач(а) запущено.")

@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ('author_username', 'published_at', 'views', 'likes', 'comments')
    list_filter = ('task',)
