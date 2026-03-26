from rest_framework import serializers
from .models import Activity, ActivityCategory, ActivityCompletion


class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = ["id", "name", "slug"]


class ActivitySerializer(serializers.ModelSerializer):
    category = ActivityCategorySerializer(read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
            "slug",
            "subtitle",
            "description",
            "instructions",
            "category",
            "min_age_months",
            "max_age_months",
            "duration_minutes",
            "difficulty",
            "is_active",
        ]


class ActivityCompletionSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)

    class Meta:
        model = ActivityCompletion
        fields = [
            "id",
            "activity",
            "difficulty",
            "note",
            "completed_at",
        ]