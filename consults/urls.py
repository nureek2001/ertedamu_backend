from django.urls import path

from .views import (
    ConsultationArticleListAPIView,
    DoctorListAPIView,
    EmergencyConsultAPIView,
    UpcomingAppointmentListAPIView,
)

urlpatterns = [
    path("doctors/", DoctorListAPIView.as_view(), name="consult-doctors"),
    path("articles/", ConsultationArticleListAPIView.as_view(), name="consult-articles"),
    path("appointments/upcoming/", UpcomingAppointmentListAPIView.as_view(), name="consult-appointments-upcoming"),
    path("emergency/", EmergencyConsultAPIView.as_view(), name="consult-emergency"),
]