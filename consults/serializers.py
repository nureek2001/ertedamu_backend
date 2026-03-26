from rest_framework import serializers

from .models import Appointment, ConsultationArticle, Doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "specialty",
            "category",
            "rating",
            "image",
            "color",
            "min_age",
            "max_age",
            "online",
        ]


class ConsultationArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationArticle
        fields = [
            "id",
            "title",
            "icon",
            "color",
            "content",
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor",
            "appointment_date",
            "appointment_time",
            "consult_type",
            "note",
        ]