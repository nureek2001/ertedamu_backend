from django.contrib import admin
from .models import ActivityCategory, Activity, ActivityCompletion


@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'min_age_months',
        'max_age_months',
        'duration_minutes',
        'is_active',
    )
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'slug')


@admin.register(ActivityCompletion)
class ActivityCompletionAdmin(admin.ModelAdmin):
    list_display = ('id', 'child', 'activity', 'difficulty', 'completed_at')
    list_filter = ('difficulty', 'completed_at')