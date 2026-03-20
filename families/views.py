from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Family,
    FamilyMembership,
    Child,
    ChildMeasurement,
    UserChildPreference,
)
from .serializers import (
    FamilySerializer,
    FamilyMembershipSerializer,
    FamilyMemberCreateSerializer,
    ChildSerializer,
    ChildCreateSerializer,
    ChildUpdateSerializer,
    ChildMeasurementSerializer,
    UserChildPreferenceSerializer,
    SetActiveChildSerializer,
)
from .utils import calculate_age_months


def get_user_family(user):
    membership = FamilyMembership.objects.select_related('family').filter(user=user).first()
    return membership.family if membership else None


def get_user_membership(user, family):
    return FamilyMembership.objects.filter(user=user, family=family).first()


def get_or_create_preference(user, family):
    preference, _ = UserChildPreference.objects.get_or_create(
        user=user,
        family=family,
        defaults={'active_child': family.children.order_by('-is_primary', 'id').first()}
    )
    return preference


class CreateMyFamilyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        existing_family = get_user_family(request.user)
        if existing_family:
            return Response({"detail": "У пользователя уже есть семья."}, status=status.HTTP_400_BAD_REQUEST)

        family = Family.objects.create(
            name=request.data.get('name', ''),
            created_by=request.user
        )

        FamilyMembership.objects.create(
            user=request.user,
            family=family,
            role='admin',
            can_edit_children=True,
            can_view_screenings=True,
            can_manage_family=True,
        )

        return Response(FamilySerializer(family).data, status=status.HTTP_201_CREATED)


class MyFamilyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        return Response(FamilySerializer(family).data)


class FamilyMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        memberships = FamilyMembership.objects.filter(family=family).select_related('user').order_by('id')
        return Response(FamilyMembershipSerializer(memberships, many=True).data)

    def post(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        membership = get_user_membership(request.user, family)
        if not membership or not membership.can_manage_family:
            return Response({"detail": "Нет прав для управления семьёй."}, status=status.HTTP_403_FORBIDDEN)

        serializer = FamilyMemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_membership = serializer.create_or_attach_user(family=family)

        return Response(FamilyMembershipSerializer(new_membership).data, status=status.HTTP_201_CREATED)


class FamilyMemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        my_membership = get_user_membership(request.user, family)
        if not my_membership or not my_membership.can_manage_family:
            return Response({"detail": "Нет прав для управления семьёй."}, status=status.HTTP_403_FORBIDDEN)

        membership = get_object_or_404(FamilyMembership, pk=pk, family=family)

        role = request.data.get('role')
        can_edit_children = request.data.get('can_edit_children')
        can_view_screenings = request.data.get('can_view_screenings')
        can_manage_family = request.data.get('can_manage_family')

        if role:
            membership.role = role
            membership.user.role = role
            membership.user.save()

        if can_edit_children is not None:
            membership.can_edit_children = bool(can_edit_children)

        if can_view_screenings is not None:
            membership.can_view_screenings = bool(can_view_screenings)

        if can_manage_family is not None:
            membership.can_manage_family = bool(can_manage_family)

        membership.save()
        return Response(FamilyMembershipSerializer(membership).data)

    def delete(self, request, pk):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        my_membership = get_user_membership(request.user, family)
        if not my_membership or not my_membership.can_manage_family:
            return Response({"detail": "Нет прав для управления семьёй."}, status=status.HTTP_403_FORBIDDEN)

        membership = get_object_or_404(FamilyMembership, pk=pk, family=family)

        if membership.user == request.user:
            return Response({"detail": "Нельзя удалить самого себя из семьи."}, status=status.HTTP_400_BAD_REQUEST)

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChildListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not get_user_membership(request.user, family):
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        children = Child.objects.filter(family=family).prefetch_related('measurements').order_by('-is_primary', 'id')
        return Response(ChildSerializer(children, many=True).data)

    def post(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        membership = get_user_membership(request.user, family)
        if not membership or not membership.can_edit_children:
            return Response({"detail": "Нет прав для добавления детей."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChildCreateSerializer(data=request.data, context={'family': family})
        serializer.is_valid(raise_exception=True)
        child = serializer.save()

        pref = UserChildPreference.objects.filter(user=request.user, family=family).first()
        if pref is None:
            UserChildPreference.objects.create(user=request.user, family=family, active_child=child)

        return Response(ChildSerializer(child).data, status=status.HTTP_201_CREATED)


class ChildDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        family = get_user_family(request.user)
        if not family:
            return None, None

        child = Child.objects.filter(pk=pk, family=family).prefetch_related('measurements').first()
        return child, family

    def get(self, request, pk):
        child, family = self.get_object(request, pk)
        if not child:
            return Response({"detail": "Ребёнок не найден."}, status=status.HTTP_404_NOT_FOUND)

        return Response(ChildSerializer(child).data)

    def patch(self, request, pk):
        child, family = self.get_object(request, pk)
        if not child:
            return Response({"detail": "Ребёнок не найден."}, status=status.HTTP_404_NOT_FOUND)

        membership = get_user_membership(request.user, family)
        if not membership or not membership.can_edit_children:
            return Response({"detail": "Нет прав для изменения ребёнка."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChildUpdateSerializer(child, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(ChildSerializer(child).data)

    def delete(self, request, pk):
        child, family = self.get_object(request, pk)
        if not child:
            return Response({"detail": "Ребёнок не найден."}, status=status.HTTP_404_NOT_FOUND)

        membership = get_user_membership(request.user, family)
        if not membership or not membership.can_edit_children:
            return Response({"detail": "Нет прав для удаления ребёнка."}, status=status.HTTP_403_FORBIDDEN)

        UserChildPreference.objects.filter(family=family, active_child=child).update(active_child=None)
        child.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ChildMeasurementListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_child(self, request, child_id):
        family = get_user_family(request.user)
        if not family:
            return None, None, None

        membership = get_user_membership(request.user, family)
        child = Child.objects.filter(pk=child_id, family=family).first()

        return child, family, membership

    def get(self, request, child_id):
        child, family, membership = self.get_child(request, child_id)
        if not child:
            return Response({"detail": "Ребёнок не найден."}, status=status.HTTP_404_NOT_FOUND)

        measurements = child.measurements.all().order_by('-measured_at')
        return Response(ChildMeasurementSerializer(measurements, many=True).data)

    def post(self, request, child_id):
        child, family, membership = self.get_child(request, child_id)
        if not child:
            return Response({"detail": "Ребёнок не найден."}, status=status.HTTP_404_NOT_FOUND)

        if not membership or not membership.can_edit_children:
            return Response({"detail": "Нет прав для добавления измерений."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChildMeasurementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        measurement = serializer.save(child=child)

        return Response(ChildMeasurementSerializer(measurement).data, status=status.HTTP_201_CREATED)


class SetActiveChildView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SetActiveChildSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        child = Child.objects.filter(
            pk=serializer.validated_data['child_id'],
            family=family
        ).first()

        if not child:
            return Response({"detail": "Ребёнок не найден в вашей семье."}, status=status.HTTP_404_NOT_FOUND)

        preference = get_or_create_preference(request.user, family)
        preference.active_child = child
        preference.save()

        return Response(UserChildPreferenceSerializer(preference).data)


class MyActiveChildView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        preference = get_or_create_preference(request.user, family)

        if preference.active_child is None:
            first_child = family.children.order_by('-is_primary', 'id').first()
            if first_child:
                preference.active_child = first_child
                preference.save()

        return Response(UserChildPreferenceSerializer(preference).data)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"detail": "Семья не найдена."}, status=status.HTTP_404_NOT_FOUND)

        membership = get_user_membership(request.user, family)
        if not membership:
            return Response({"detail": "Нет доступа к семье."}, status=status.HTTP_403_FORBIDDEN)

        preference = get_or_create_preference(request.user, family)
        active_child = preference.active_child

        if active_child is None:
            active_child = family.children.order_by('-is_primary', 'id').first()
            if active_child:
                preference.active_child = active_child
                preference.save()

        if active_child is None:
            return Response({
                "active_child": None,
                "latest_measurement": None,
                "total_children": family.children.count(),
                "family_members_count": family.memberships.count(),
                "active_child_age_months": None,
            })

        latest_measurement = active_child.measurements.order_by('-measured_at').first()

        data = {
            "active_child": ChildSerializer(active_child).data,
            "latest_measurement": ChildMeasurementSerializer(latest_measurement).data if latest_measurement else None,
            "total_children": family.children.count(),
            "family_members_count": family.memberships.count(),
            "active_child_age_months": calculate_age_months(active_child.birth_date),
        }
        return Response(data)