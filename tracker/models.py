from django.conf import settings
from django.db import models


class ShowEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='entries',
    )

    TYPE_CHOICES = [
        ("movie", "Movie"),
        ("tv", "TV Series"),
        ("anime", "Anime"),
    ]
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("watching", "Watching"),
        ("planned", "Plan to watch"),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="movie")
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    date_watched = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="completed")
    ep_current = models.IntegerField(null=True, blank=True)
    ep_total = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_watched", "-created_at"]

    def __str__(self):
        return self.title