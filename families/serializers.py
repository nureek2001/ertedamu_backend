from django.db import transaction
from rest_framework import serializers

from accounts.models import User
from accounts.serializers import UserSerializer
from .models import (
    Family,
    FamilyMembership,
    Child,
    ChildMeasurement,
    UserChildPreference,
)
from .utils import calculate_age_months


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ['id', 'name', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class FamilyMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = FamilyMembership
        fields = [
            'id',
            'user',
            'family',
            'role',
            'can_edit_children',
            'can_view_screenings',
            'can_manage_family',
            'joined_at',
        ]
        read_only_fields = ['id', 'family', 'joined_at']


class FamilyMemberCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    full_name = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(choices=FamilyMembership.ROLE_CHOICES)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    can_edit_children = serializers.BooleanField(default=False)
    can_view_screenings = serializers.BooleanField(default=True)
    can_manage_family = serializers.BooleanField(default=False)

    def validate_email(self, value):
        return value.lower().strip()

    @transaction.atomic
    def create_or_attach_user(self, family):
        validated_data = self.validated_data
        email = validated_data['email']

        user = User.objects.filter(email=email).first()

        if user is None:
            raw_password = validated_data.get('password') or 'TempPass12345'
            user = User.objects.create_user(
                email=email,
                phone=validated_data.get('phone'),
                full_name=validated_data['full_name'],
                role=validated_data['role'],
                password=raw_password,
            )
        else:
            if not user.full_name and validated_data.get('full_name'):
                user.full_name = validated_data['full_name']
            if not user.phone and validated_data.get('phone'):
                user.phone = validated_data['phone']
            if user.role != 'admin':
                user.role = validated_data['role']
            user.save()

        membership, created = FamilyMembership.objects.get_or_create(
            user=user,
            family=family,
            defaults={
                'role': validated_data['role'],
                'can_edit_children': validated_data['can_edit_children'],
                'can_view_screenings': validated_data['can_view_screenings'],
                'can_manage_family': validated_data['can_manage_family'],
            }
        )

        if not created:
            raise serializers.ValidationError("Этот пользователь уже состоит в семье.")

        return membership


class ChildMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildMeasurement
        fields = ['id', 'height', 'weight', 'measured_at', 'note']
        read_only_fields = ['id', 'measured_at']


class ChildSerializer(serializers.ModelSerializer):
    age_months = serializers.SerializerMethodField()
    latest_measurement = serializers.SerializerMethodField()

    class Meta:
        model = Child
        fields = [
            'id',
            'family',
            'first_name',
            'birth_date',
            'gender',
            'is_primary',
            'created_at',
            'age_months',
            'latest_measurement',
        ]
        read_only_fields = ['id', 'family', 'created_at', 'age_months', 'latest_measurement']

    def get_age_months(self, obj):
        return calculate_age_months(obj.birth_date)

    def get_latest_measurement(self, obj):
        latest = obj.measurements.order_by('-measured_at').first()
        if not latest:
            return None
        return ChildMeasurementSerializer(latest).data


class ChildCreateSerializer(serializers.ModelSerializer):
    initial_height = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    initial_weight = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)

    class Meta:
        model = Child
        fields = [
            'id',
            'first_name',
            'birth_date',
            'gender',
            'is_primary',
            'initial_height',
            'initial_weight',
        ]
        read_only_fields = ['id']

    @transaction.atomic
    def create(self, validated_data):
        initial_height = validated_data.pop('initial_height', None)
        initial_weight = validated_data.pop('initial_weight', None)
        family = self.context['family']

        if validated_data.get('is_primary'):
            Child.objects.filter(family=family, is_primary=True).update(is_primary=False)

        child = Child.objects.create(family=family, **validated_data)

        if initial_height is not None or initial_weight is not None:
            ChildMeasurement.objects.create(
                child=child,
                height=initial_height,
                weight=initial_weight,
            )

        return child


class ChildUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['first_name', 'birth_date', 'gender', 'is_primary']

    def update(self, instance, validated_data):
        if validated_data.get('is_primary'):
            Child.objects.filter(family=instance.family, is_primary=True).exclude(pk=instance.pk).update(is_primary=False)
        return super().update(instance, validated_data)


class UserChildPreferenceSerializer(serializers.ModelSerializer):
    active_child = ChildSerializer(read_only=True)

    class Meta:
        model = UserChildPreference
        fields = ['id', 'user', 'family', 'active_child', 'updated_at']
        read_only_fields = ['id', 'user', 'family', 'updated_at']


class SetActiveChildSerializer(serializers.Serializer):
    child_id = serializers.IntegerField()

    def validate_child_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Неверный child_id")
        return value


class DashboardSerializer(serializers.Serializer):
    active_child = ChildSerializer()
    latest_measurement = ChildMeasurementSerializer(allow_null=True)
    total_children = serializers.IntegerField()
    family_members_count = serializers.IntegerField()
    active_child_age_months = serializers.IntegerField()