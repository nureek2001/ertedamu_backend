from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from families.models import Child, FamilyMembership
from families.utils import calculate_age_months
from .models import ActivityCategory, Activity, ActivityCompletion
from .serializers import (
    ActivityCategorySerializer,
    ActivitySerializer,
    ActivityCompletionSerializer,
    ActivityCompletionCreateSerializer,
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


class ActivityCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = ActivityCategory.objects.all()
        return Response(ActivityCategorySerializer(categories, many=True).data)


class ActivityListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Activity.objects.filter(is_active=True).select_related('category')

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

        return Response(ActivitySerializer(queryset, many=True).data)


class ActivityDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, activity_id):
        activity = Activity.objects.filter(pk=activity_id, is_active=True).select_related('category').first()
        if not activity:
            return Response({"detail": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

        return Response(ActivitySerializer(activity).data)


class ActivityCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, activity_id):
        activity = Activity.objects.filter(pk=activity_id, is_active=True).select_related('category').first()
        if not activity:
            return Response({"detail": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ActivityCompletionCreateSerializer(
            data=request.data,
            context={'request': request, 'activity': activity}
        )
        serializer.is_valid(raise_exception=True)
        completion = serializer.save()

        return Response(ActivityCompletionSerializer(completion).data, status=status.HTTP_201_CREATED)


class ChildActivityHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, child_id):
        child, membership = get_child_for_user(request.user, child_id)
        if not child:
            return Response({"detail": "Ребёнок не найден или нет доступа."}, status=status.HTTP_404_NOT_FOUND)

        queryset = ActivityCompletion.objects.filter(
            child=child
        ).select_related(
            'activity', 'activity__category'
        )

        difficulty = request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        return Response(ActivityCompletionSerializer(queryset, many=True).data)