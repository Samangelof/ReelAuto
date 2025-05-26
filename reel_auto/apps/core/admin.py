import os
from django.contrib import admin
from django.utils.html import format_html
from .models import SearchTask, SearchResult
from core.tasks import run_search_task_async


@admin.register(SearchTask)
class SearchTaskAdmin(admin.ModelAdmin):
    # list_display = ('keywords', 'created_at', 'colored_status', 'download_link')
    list_display = ('keywords', 'created_at', 'colored_status', 'results_link', 'download_link')

    actions = ['run_task_now']

    @admin.action(description="Запустить задачу сейчас")
    def run_task_now(self, request, queryset):
        for task in queryset:
            task.status = 'pending'
            task.save()
            run_search_task_async.delay(task.id)
        self.message_user(request, f"{queryset.count()} задач(а) отправлено на выполнение")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # только при создании
            obj.status = 'pending'
            obj.save()
            run_search_task_async.delay(obj.id)


    def colored_status(self, obj):
        color = {
            'done': 'green',
            'error': 'red',
            'processing': 'orange',
            'pending': 'gray'
        }.get(obj.status, 'black')
        return format_html('<b style="color:{};">{}</b>', color, obj.get_status_display())


    colored_status.short_description = "Статус"


    def results_link(self, obj):
        if obj.results.exists():
            return format_html('<a href="/admin/core/searchresult/?task__id__exact={}">Открыть</a>', obj.id)
        return "-"
    results_link.short_description = "Результаты"


    def download_link(self, obj):
        if obj.csv_file and obj.csv_file.storage.exists(obj.csv_file.name):
            full_path = obj.csv_file.path
            if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                return format_html('<a href="{}">Скачать</a>', obj.csv_file.url)
        return "-"

@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ('task', 'author_username', 'published_at', 'views', 'likes', 'comments')
    list_filter = ('task',)
