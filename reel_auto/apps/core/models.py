from django.db import models


class SearchTask(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'В очереди'),
            ('processing', 'Обрабатывается'),
            ('done', 'Завершено'),
            ('error', 'Ошибка')
        ],
        default='pending',
        verbose_name="Статус"
    )

    views_from = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Минимум просмотров"
    )

    likes_from = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Минимум лайков"
    )

    comments_from = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Минимум комментариев"
    )

    date_from = models.DateField(
        null=True, blank=True,
        verbose_name="Дата от"
    )

    date_to = models.DateField(
        null=True, blank=True,
        verbose_name="Дата до"
    )

    keywords = models.TextField(
        null=True, blank=True,
        verbose_name="Ключевые слова или хэштеги"
    )

    limit = models.PositiveIntegerField(
        default=50,
        verbose_name="Лимит на количество результатов"
    )

    csv_file = models.FileField(
        upload_to='exports/',
        null=True, blank=True,
        verbose_name="Готовый CSV-файл"
    )

    error_message = models.TextField(
        blank=True, null=True,
        verbose_name="Сообщение об ошибке"
    )

    def __str__(self):
        return f"Поиск по: {self.keywords} | #{self.id} | от {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Поиск reel"
        verbose_name_plural = "Поиск reels"


class SearchResult(models.Model):
    task = models.ForeignKey(
        SearchTask,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name="Задача"
    )

    video_url = models.URLField(
        max_length=2048, verbose_name="Ссылка на видео")
    author_username = models.CharField(
        max_length=500, verbose_name="Никнейм автора")
    published_at = models.DateTimeField(verbose_name="Дата публикации")
    description = models.TextField(blank=True, verbose_name="Описание поста")
    hashtags = models.TextField(blank=True, verbose_name="Хэштеги")
    views = models.PositiveIntegerField(verbose_name="Количество просмотров")
    likes = models.PositiveIntegerField(verbose_name="Количество лайков")
    comments = models.PositiveIntegerField(
        verbose_name="Количество комментариев")
    sound_url = models.URLField(
        max_length=2048, blank=True, null=True, verbose_name="Ссылка на звук")

    class Meta:
        verbose_name = "Найденный Reels"
        verbose_name_plural = "Найденные Reels"


class SearchRawResult(models.Model):
    task = models.ForeignKey(SearchTask, on_delete=models.CASCADE, related_name="raw_results")
    video_url = models.URLField(max_length=2048, blank=True, null=True)
    author_username = models.CharField(max_length=500, blank=True, null=True)
    published_at = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    hashtags = models.TextField(blank=True, null=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    sound_url = models.URLField(max_length=2048, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сырой рилс"
        verbose_name_plural = "Сырые рилсы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author_username or '—'} | {self.video_url or 'без ссылки'}"