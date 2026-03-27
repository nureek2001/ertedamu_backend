from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from families.models import Child, FamilyMembership
from .models import Activity, ActivityCategory, ActivityCompletion
from .serializers import ActivitySerializer, ActivityCompletionSerializer, ActivityCategorySerializer
from families.utils import calculate_age_months

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

class ActivityCategoryListAPIView(generics.ListAPIView):
    queryset = ActivityCategory.objects.all()
    serializer_class = ActivityCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ActivityListAPIView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Activity.objects.filter(is_active=True).select_related("category")

        child_id = self.request.query_params.get("child_id")
        category = self.request.query_params.get("category")
        month = self.request.query_params.get("month")

        if category and category != "all":
            queryset = queryset.filter(category__slug=category)

        if month:
            try:
                month = int(month)
                queryset = queryset.filter(
                    min_age_months__lte=month,
                    max_age_months__gte=month,
                )
            except ValueError:
                pass

        if child_id:
            child, membership = get_child_for_user(self.request.user, child_id)
            age_months = calculate_age_months(child.birth_date)

            if child:
                queryset = queryset.filter(
                    min_age_months__lte=age_months,
                    max_age_months__gte=age_months,
                )
            else:
                return Response({"detail": "Ребёнок не найден или нет доступа."}, status=status.HTTP_404_NOT_FOUND)


        return queryset


class ActivityDetailAPIView(generics.RetrieveAPIView):
    queryset = Activity.objects.filter(is_active=True).select_related("category")
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]


class ActivityCompletionCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, activity_slug):
        child_id = request.data.get("child_id")
        print(child_id)
        difficulty = request.data.get("difficulty")
        note = request.data.get("note")
        child, membership = get_child_for_user(request.user, child_id)
        if not child:
            return Response({"detail": "Ребёнок не найден."}, status=status.HTTP_404_NOT_FOUND)

        activity = Activity.objects.filter(slug = activity_slug, is_active=True).first()
        if not activity:
            return Response({"detail": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

        completion = ActivityCompletion.objects.create(
            child=child,
            activity=activity,
            difficulty=difficulty,
            note=note,
        )
        return Response(ActivityCompletionSerializer(completion).data, status=status.HTTP_201_CREATED)


class ChildActivityHistoryAPIView(generics.ListAPIView):
    serializer_class = ActivityCompletionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        child_id = self.kwargs["child_id"]
        child, membership = get_child_for_user(self.request.user, child_id)
        print(child)
        if not child:
            return ActivityCompletion.objects.none()
        print(ActivityCompletion.objects.filter(child=child).count())
        return ActivityCompletion.objects.filter(
            child = child
        ).select_related("activity", "activity__category").distinct()