from django.utils import timezone
from rest_framework import serializers

from families.models import Child, FamilyMembership
from families.utils import calculate_age_months
from .models import MilestoneCategory, Milestone, ChildMilestoneProgress


class MilestoneCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneCategory
        fields = ['id', 'name', 'slug']


class MilestoneSerializer(serializers.ModelSerializer):
    category = MilestoneCategorySerializer(read_only=True)

    class Meta:
        model = Milestone
        fields = [
            'id',
            'title',
            'description',
            'category',
            'min_age_months',
            'max_age_months',
            'is_active',
        ]


class ChildMilestoneProgressSerializer(serializers.ModelSerializer):
    milestone = MilestoneSerializer(read_only=True)

    class Meta:
        model = ChildMilestoneProgress
        fields = [
            'id',
            'milestone',
            'is_completed',
            'confirmed_at',
            'note',
        ]


class MilestoneToggleSerializer(serializers.Serializer):
    child_id = serializers.IntegerField()
    is_completed = serializers.BooleanField()
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_child_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Некорректный child_id.")
        return value

    def validate(self, attrs):
        request = self.context['request']
        milestone = self.context['milestone']

        child = Child.objects.filter(pk=attrs['child_id']).select_related('family').first()
        if not child:
            raise serializers.ValidationError({"child_id": "Ребёнок не найден."})

        membership = FamilyMembership.objects.filter(
            user=request.user,
            family=child.family
        ).first()
        if not membership or not membership.can_edit_children:
            raise serializers.ValidationError({"detail": "Нет прав для изменения milestone."})

        age_months = calculate_age_months(child.birth_date)
        if not (milestone.min_age_months <= age_months <= milestone.max_age_months):
            raise serializers.ValidationError({
                "detail": "Возраст ребёнка не подходит для этого milestone."
            })

        attrs['child'] = child
        return attrs

    def save_progress(self):
        milestone = self.context['milestone']
        child = self.validated_data['child']
        is_completed = self.validated_data['is_completed']
        note = self.validated_data.get('note')

        progress, _ = ChildMilestoneProgress.objects.get_or_create(
            child=child,
            milestone=milestone
        )

        progress.is_completed = is_completed
        progress.note = note

        if is_completed:
            progress.confirmed_at = timezone.now()
        else:
            progress.confirmed_at = None

        progress.save()
        return progress