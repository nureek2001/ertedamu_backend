from datetime import date

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from families.utils import calculate_age_months

from families.models import Child, FamilyMembership
from .models import Appointment, ConsultationArticle, Doctor
from .serializers import (
    AppointmentSerializer,
    ConsultationArticleSerializer,
    DoctorSerializer,
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

class DoctorListAPIView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Doctor.objects.filter(is_active=True)

        category = self.request.query_params.get("category")
        child_id = self.request.query_params.get("child_id")

        if category and category != "all":
            queryset = queryset.filter(category=category)

        if child_id:
            child, membership = get_child_for_user(self.request.user, child_id)
            if not child:
                return Response({"detail": "Ребёнок не найден или нет доступа."}, status=status.HTTP_404_NOT_FOUND)
            age_months = calculate_age_months(child.birth_date)
            
            queryset = queryset.filter(
                min_age__lte=age_months,
                max_age__gte=age_months,
            )

        return queryset


class ConsultationArticleListAPIView(generics.ListAPIView):
    serializer_class = ConsultationArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ConsultationArticle.objects.filter(is_active=True)


class UpcomingAppointmentListAPIView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        child_id = self.request.query_params.get("child_id")

        queryset = Appointment.objects.filter(
            is_active=True,
            child__pk=child_id,
            appointment_date__gte=date.today(),
        ).select_related("doctor", "child").distinct()

        if child_id:
            queryset = queryset.filter(child_id=child_id)

        return queryset[:5]


class EmergencyConsultAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({
            "message": "Соединяем с дежурным педиатром..."
        })