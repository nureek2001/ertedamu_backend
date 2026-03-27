from django.utils import timezone
from rest_framework import serializers

from families.models import Child, FamilyMembership
from families.utils import calculate_age_months
from .models import MilestoneCategory, Milestone, ChildMilestoneProgress
from families.permissions import get_membership

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

    def validate(self, attrs):
        request = self.context['request']
        milestone = self.context['milestone']
        child_id = attrs['child_id']

        child = Child.objects.filter(pk=child_id).select_related('family').first()
        if not child:
            raise serializers.ValidationError({"child_id": "Ребёнок не найден."})

        membership = get_membership(request.user, child.family)
        if not membership:
            raise serializers.ValidationError({"detail": "Нет доступа к ребёнку."})

        if not membership.can_edit_children:
            raise serializers.ValidationError({"detail": "Нет прав для изменения milestones."})

        # ВАЖНО:
        # Больше НЕ проверяем возраст ребёнка против milestone,
        # потому что фронт теперь показывает milestones по таймлайну,
        # а не только по текущему месяцу ребёнка.

        attrs['child'] = child
        attrs['milestone'] = milestone
        return attrs

    def save_progress(self):
        child = self.validated_data['child']
        milestone = self.validated_data['milestone']
        is_completed = self.validated_data['is_completed']
        note = self.validated_data.get('note')

        progress, _ = ChildMilestoneProgress.objects.get_or_create(
            child=child,
            milestone=milestone,
            defaults={
                'is_completed': False,
                'note': None,
                'confirmed_at': None,
            }
        )

        progress.is_completed = is_completed
        progress.note = note

        if is_completed:
            progress.confirmed_at = timezone.now()
        else:
            progress.confirmed_at = None

        progress.save(update_fields=['is_completed', 'note', 'confirmed_at'])
        return progress

class MilestoneProgressItemSerializer(serializers.Serializer):
    milestone = MilestoneSerializer()
    progress = ChildMilestoneProgressSerializer(allow_null=True)


class ChildMilestoneProgressResponseSerializer(serializers.Serializer):
    child_id = serializers.IntegerField()
    total = serializers.IntegerField()
    completed = serializers.IntegerField()
    percent = serializers.IntegerField()
    items = MilestoneProgressItemSerializer(many=True)