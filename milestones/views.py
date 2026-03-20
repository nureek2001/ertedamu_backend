from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from families.models import Child, FamilyMembership
from families.utils import calculate_age_months
from .models import MilestoneCategory, Milestone, ChildMilestoneProgress
from .serializers import (
    MilestoneCategorySerializer,
    MilestoneSerializer,
    ChildMilestoneProgressSerializer,
    MilestoneToggleSerializer,
)


def get_child_for_user(user, child_id):
    child = Child.objects.filter(pk=child_id).select_related('family').first()
    if not child:
        return None, None

    membership = FamilyMembership.objects.filter(
        user=user,
        family=child.family
    ).first()

    if not membership:
        return None, None

    return child, membership


class MilestoneCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = MilestoneCategory.objects.all()
        return Response(MilestoneCategorySerializer(categories, many=True).data)


class MilestoneListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Milestone.objects.filter(is_active=True).select_related('category')

        category_slug = request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        child_id = request.query_params.get('child_id')
        if child_id:
            child, membership = get_child_for_user(request.user, child_id)
            if not child:
                return Response({"detail": "Ребёнок не найден или нет доступа."}, status=status.HTTP_404_NOT_FOUND)

            age_months = calculate_age_months(child.birth_date)
            queryset = queryset.filter(
                min_age_months__lte=age_months,
                max_age_months__gte=age_months
            )

        return Response(MilestoneSerializer(queryset, many=True).data)


class MilestoneDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, milestone_id):
        milestone = Milestone.objects.filter(pk=milestone_id, is_active=True).select_related('category').first()
        if not milestone:
            return Response({"detail": "Milestone не найден."}, status=status.HTTP_404_NOT_FOUND)

        return Response(MilestoneSerializer(milestone).data)


class MilestoneToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, milestone_id):
        milestone = Milestone.objects.filter(pk=milestone_id, is_active=True).select_related('category').first()
        if not milestone:
            return Response({"detail": "Milestone не найден."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MilestoneToggleSerializer(
            data=request.data,
            context={'request': request, 'milestone': milestone}
        )
        serializer.is_valid(raise_exception=True)
        progress = serializer.save_progress()

        return Response(ChildMilestoneProgressSerializer(progress).data)


class ChildMilestoneProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, child_id):
        child, membership = get_child_for_user(request.user, child_id)
        if not child:
            return Response({"detail": "Ребёнок не найден или нет доступа."}, status=status.HTTP_404_NOT_FOUND)

        age_months = calculate_age_months(child.birth_date)

        milestones = Milestone.objects.filter(
            is_active=True,
            min_age_months__lte=age_months,
            max_age_months__gte=age_months
        ).select_related('category')

        progress_map = {
            item.milestone_id: item
            for item in ChildMilestoneProgress.objects.filter(
                child=child,
                milestone__in=milestones
            ).select_related('milestone', 'milestone__category')
        }

        data = []
        completed = 0

        for milestone in milestones:
            progress = progress_map.get(milestone.id)
            is_completed = progress.is_completed if progress else False
            if is_completed:
                completed += 1

            data.append({
                "milestone": MilestoneSerializer(milestone).data,
                "progress": ChildMilestoneProgressSerializer(progress).data if progress else None,
            })

        total = len(data)
        percent = round((completed / total) * 100, 2) if total else 0

        return Response({
            "child_id": child.id,
            "total": total,
            "completed": completed,
            "percent": percent,
            "items": data,
        })