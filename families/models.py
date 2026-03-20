from django.conf import settings
from django.db import models


class Family(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_families'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Family #{self.id}"


class FamilyMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('grandmother', 'Grandmother'),
        ('grandfather', 'Grandfather'),
        ('relative', 'Relative'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='family_memberships'
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    can_edit_children = models.BooleanField(default=False)
    can_view_screenings = models.BooleanField(default=True)
    can_manage_family = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'family')

    def __str__(self):
        return f"{self.user} - {self.family}"


class Child(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='children'
    )
    first_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name


class ChildMeasurement(models.Model):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='measurements'
    )
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    measured_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-measured_at']

    def __str__(self):
        return f"{self.child.first_name} - {self.measured_at:%Y-%m-%d}"


class UserChildPreference(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='child_preferences'
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='user_preferences'
    )
    active_child = models.ForeignKey(
        Child,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='active_for_users'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'family')

    def __str__(self):
        return f"{self.user} active child -> {self.active_child}"