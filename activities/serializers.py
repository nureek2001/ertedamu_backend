from rest_framework import serializers
from families.models import Child, FamilyMembership
from families.utils import calculate_age_months
from .models import ActivityCategory, Activity, ActivityCompletion


class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = ['id', 'name', 'slug']


class ActivitySerializer(serializers.ModelSerializer):
    category = ActivityCategorySerializer(read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'instructions',
            'category',
            'min_age_months',
            'max_age_months',
            'duration_minutes',
            'is_active',
        ]


class ActivityCompletionSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)

    class Meta:
        model = ActivityCompletion
        fields = [
            'id',
            'activity',
            'difficulty',
            'note',
            'completed_at',
        ]


class ActivityCompletionCreateSerializer(serializers.Serializer):
    child_id = serializers.IntegerField()
    difficulty = serializers.ChoiceField(choices=ActivityCompletion.DIFFICULTY_CHOICES, default='ok')
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_child_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Некорректный child_id.")
        return value

    def validate(self, attrs):
        request = self.context['request']
        activity = self.context['activity']

        child = Child.objects.filter(pk=attrs['child_id']).select_related('family').first()
        if not child:
            raise serializers.ValidationError({"child_id": "Ребёнок не найден."})

        membership = FamilyMembership.objects.filter(
            user=request.user,
            family=child.family
        ).first()
        if not membership:
            raise serializers.ValidationError({"detail": "Нет доступа к ребёнку."})

        age_months = calculate_age_months(child.birth_date)
        if not (activity.min_age_months <= age_months <= activity.max_age_months):
            raise serializers.ValidationError({
                "detail": "Возраст ребёнка не подходит для этой активности."
            })

        attrs['child'] = child
        return attrs

    def create(self, validated_data):
        activity = self.context['activity']
        child = validated_data['child']

        return ActivityCompletion.objects.create(
            child=child,
            activity=activity,
            difficulty=validated_data.get('difficulty', 'ok'),
            note=validated_data.get('note'),
        )