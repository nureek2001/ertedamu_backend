from django.contrib import admin

from .models import Appointment, ConsultationArticle, Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "category", "rating", "online", "is_active", "order")
    list_filter = ("category", "online", "is_active")
    search_fields = ("name", "specialty")


@admin.register(ConsultationArticle)
class ConsultationArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order")
    search_fields = ("title",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("child", "doctor", "appointment_date", "appointment_time", "consult_type", "is_active")
    list_filter = ("consult_type", "is_active")