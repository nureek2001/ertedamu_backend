from django.contrib import admin
from .models import Family, FamilyMembership, Child, ChildMeasurement, UserChildPreference


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'created_at')
    search_fields = ('name', 'created_by__email', 'created_by__full_name')


@admin.register(FamilyMembership)
class FamilyMembershipAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'family',
        'role',
        'can_edit_children',
        'can_view_screenings',
        'can_manage_family',
        'joined_at',
    )
    list_filter = ('role', 'can_edit_children', 'can_manage_family')


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'family', 'birth_date', 'gender', 'is_primary', 'created_at')
    list_filter = ('gender', 'is_primary')


@admin.register(ChildMeasurement)
class ChildMeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'child', 'height', 'weight', 'measured_at')
    list_filter = ('measured_at',)


@admin.register(UserChildPreference)
class UserChildPreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'family', 'active_child', 'updated_at')