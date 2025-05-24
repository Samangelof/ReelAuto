# core/admin.py
from django.contrib import admin
from .models import SearchTask, SearchResult
from core.tasks import run_search_task as run_search_task_async
# from .services.task_runner import run_search_task


@admin.register(SearchTask)
class SearchTaskAdmin(admin.ModelAdmin):
    list_display = ('keywords', 'created_at', 'status')
    actions = ['run_task_now']

    @admin.action(description="Запустить задачу сейчас")
    def run_task_now(self, request, queryset):
        for task in queryset:
            task.status = 'pending'
            task.save()
            run_search_task_async.delay(task.id)  # теперь в фоне
        self.message_user(request, f"{queryset.count()} задач(а) отправлено на выполнение")
            

@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ('task', 'author_username', 'published_at', 'views', 'likes', 'comments')
    list_filter = ('task',)
