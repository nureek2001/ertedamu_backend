from rest_framework.permissions import BasePermission
from .models import FamilyMembership


def get_membership(user, family):
    return FamilyMembership.objects.filter(user=user, family=family).first()


class IsFamilyMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        family = getattr(obj, 'family', None)
        if family is None:
            return False
        return FamilyMembership.objects.filter(user=request.user, family=family).exists()


class CanManageFamily(BasePermission):
    def has_permission(self, request, view):
        family = getattr(view, 'family', None)
        if family is None:
            return False

        membership = get_membership(request.user, family)
        return bool(membership and membership.can_manage_family)


class CanEditChildren(BasePermission):
    def has_permission(self, request, view):
        family = getattr(view, 'family', None)
        if family is None:
            return False

        membership = get_membership(request.user, family)
        return bool(membership and membership.can_edit_children)