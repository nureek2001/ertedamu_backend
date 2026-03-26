from django.conf import settings
from django.db import models


class ActivityCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Activity(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Легко"),
        ("ok", "Средне"),
        ("hard", "Сложно"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        ActivityCategory,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    min_age_months = models.PositiveIntegerField(default=0)
    max_age_months = models.PositiveIntegerField(default=72)
    duration_minutes = models.PositiveIntegerField(default=10)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="easy")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class ActivityCompletion(models.Model):
    child = models.ForeignKey(
        "families.Child",
        on_delete=models.CASCADE,
        related_name="activity_completions"
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="completions"
    )
    difficulty = models.CharField(max_length=10, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]