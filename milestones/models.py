from django.db import models
from families.models import Child


class MilestoneCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Milestone categories'

    def __str__(self):
        return self.name


class Milestone(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    category = models.ForeignKey(
        MilestoneCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milestones'
    )

    min_age_months = models.PositiveIntegerField(default=0)
    max_age_months = models.PositiveIntegerField(default=999)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


class ChildMilestoneProgress(models.Model):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='milestone_progress'
    )
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.CASCADE,
        related_name='child_progress'
    )
    is_completed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('child', 'milestone')
        ordering = ['milestone__id']

    def __str__(self):
        return f"{self.child} - {self.milestone} - {self.is_completed}"