from django.db import models
from families.models import Child


class ActivityCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Activity categories'

    def __str__(self):
        return self.name


class Activity(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    instructions = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        ActivityCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )

    min_age_months = models.PositiveIntegerField(default=0)
    max_age_months = models.PositiveIntegerField(default=999)

    duration_minutes = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


class ActivityCompletion(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('ok', 'OK'),
        ('hard', 'Hard'),
    ]

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='activity_completions'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='ok')
    note = models.CharField(max_length=255, blank=True, null=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.child} - {self.activity} - {self.completed_at:%Y-%m-%d}"