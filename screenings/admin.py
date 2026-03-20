from django.contrib import admin
from .models import ScreeningTemplate, ScreeningQuestion, ScreeningSession, ScreeningAnswer


class ScreeningQuestionInline(admin.TabularInline):
    model = ScreeningQuestion
    extra = 0


@admin.register(ScreeningTemplate)
class ScreeningTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'code',
        'template_type',
        'min_age_months',
        'max_age_months',
        'cooldown_days',
        'is_active',
    )
    list_filter = ('template_type', 'is_active')
    inlines = [ScreeningQuestionInline]


@admin.register(ScreeningQuestion)
class ScreeningQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'template', 'order', 'answer_type', 'risk_answer', 'is_required')
    list_filter = ('template', 'answer_type')


@admin.register(ScreeningSession)
class ScreeningSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'child',
        'template',
        'status',
        'result_level',
        'score',
        'started_at',
        'completed_at',
    )
    list_filter = ('template', 'status', 'result_level')


@admin.register(ScreeningAnswer)
class ScreeningAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'question', 'answer_value')
    list_filter = ('question__template',)