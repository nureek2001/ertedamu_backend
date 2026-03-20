from django.db import models
from django.utils import timezone

from families.models import Child


class ScreeningTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('mchat', 'M-CHAT'),
        ('early_dev', 'Early Development'),
    ]

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, default='mchat')
    description = models.TextField(blank=True, null=True)

    min_age_months = models.PositiveIntegerField(default=0)
    max_age_months = models.PositiveIntegerField(default=999)

    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)

    cooldown_days = models.PositiveIntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.title} ({self.code})"


class ScreeningQuestion(models.Model):
    ANSWER_TYPES = [
        ('yes_no', 'Yes / No'),
        ('single_choice', 'Single Choice'),
    ]

    template = models.ForeignKey(
        ScreeningTemplate,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    order = models.PositiveIntegerField()
    text = models.TextField()
    answer_type = models.CharField(max_length=30, choices=ANSWER_TYPES, default='yes_no')

    # Для M-CHAT: какое значение считается рисковым
    # yes / no
    risk_answer = models.CharField(max_length=20, blank=True, null=True)

    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ('template', 'order')

    def __str__(self):
        return f"{self.template.code} - Q{self.order}"


class ScreeningSession(models.Model):
    RESULT_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('done', 'Done'),
        ('unknown', 'Unknown'),
    ]

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='screening_sessions'
    )
    template = models.ForeignKey(
        ScreeningTemplate,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    result_level = models.CharField(max_length=20, choices=RESULT_LEVELS, default='unknown')
    score = models.PositiveIntegerField(default=0)

    target_age_months = models.PositiveIntegerField(blank=True, null=True)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.child.first_name} - {self.template.code} - {self.status}"

    def complete(self, score, result_level):
        self.score = score
        self.result_level = result_level
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['score', 'result_level', 'status', 'completed_at'])


class ScreeningAnswer(models.Model):
    session = models.ForeignKey(
        ScreeningSession,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        ScreeningQuestion,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    answer_value = models.CharField(max_length=50)

    class Meta:
        unique_together = ('session', 'question')
        ordering = ['question__order']

    def __str__(self):
        return f"Session {self.session_id} - Q{self.question.order}"