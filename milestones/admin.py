from django.contrib import admin
from .models import MilestoneCategory, Milestone, ChildMilestoneProgress


@admin.register(MilestoneCategory)
class MilestoneCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'min_age_months',
        'max_age_months',
        'is_active',
    )
    list_filter = ('category', 'is_active')


@admin.register(ChildMilestoneProgress)
class ChildMilestoneProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'child', 'milestone', 'is_completed', 'confirmed_at')
    list_filter = ('is_completed', 'confirmed_at')