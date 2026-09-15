from django.conf import settings
from django.core.exceptions import ValidationError
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
        ("dropped", "Dropped"),
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
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "type"]),
            models.Index(fields=["user", "-date_watched"]),
        ]
        verbose_name = "Show Entry"
        verbose_name_plural = "Show Entries"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.rating is not None and not (0 <= self.rating <= 10):
            raise ValidationError({"rating": "Rating must be between 0 and 10."})
        if self.ep_current is not None and self.ep_total is not None:
            if self.ep_current < 0:
                raise ValidationError({"ep_current": "Episode count cannot be negative."})
            if self.ep_total < 0:
                raise ValidationError({"ep_total": "Total episodes cannot be negative."})
            if self.ep_current > self.ep_total:
                raise ValidationError(
                    {"ep_current": "Current episode cannot exceed total episodes."}
                )
        if self.year is not None and self.year < 1888:
            raise ValidationError({"year": "Year seems too early. Please check."})